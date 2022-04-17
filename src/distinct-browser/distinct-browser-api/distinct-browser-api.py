#!/usr/bin/env python3

import logging
import sys
import subprocess
import os
import shutil
import json
import base64
from threading import Thread
from functools import wraps
from socket import socket
from flask import Flask, request
from flask_cors import CORS

logger = logging.getLogger(__name__)

class BrowserAPI(Thread):

    def __init__(self):
        logger.info("Initializing browser api thread")
        super(BrowserAPI, self).__init__()

        self.app = Flask(__name__)
        self.app.url_map.strict_slashes = False # allow trailing slashes
        CORS(self.app, resources={r"/api/*": {"origins": "*"}}) # enable CORS
        self.register_routes()

        self.browsers_by_handler = {} # {handler_uuid: Pprocess, ...}
        self.proxies_by_handler = {} # {handler_uuid: Pprocess, ...}

    def run(self):
        logger.info("Starting browser api thread")

        listen_host = "0.0.0.0"
        listen_port = 8080

        logger.info(f"Starting webserver on {listen_host}:{listen_port}")
        self.app.run(host=listen_host, port=listen_port)

    def register_routes(self):
        logger.info("Registering routes for the browser api's webserver")

        self.app.add_url_rule(
            "/api/browsers", view_func=self.api_browsers, methods=["GET"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>", view_func=self.api_browsers_handler, methods=["GET"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>/start", view_func=self.api_browsers_start, methods=["POST"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>/stop", view_func=self.api_browsers_stop, methods=["POST"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>/profile", view_func=self.api_browsers_profile, methods=["GET"]
        )
        self.app.add_url_rule(
            "/api/proxies/<handler_uuid>/stream", view_func=self.api_proxies_stream, methods=["GET"]
        )
        self.app.add_url_rule(
            "/api/proxies/<handler_uuid>/har", view_func=self.api_proxies_har, methods=["GET"]
        )

    """ Routines """

    @staticmethod
    def get_free_port():
        with socket() as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def setup_chrome_extensions(self, handler_uuid):
        """ Setup chrome extensions for handler """
        distinct_ext_for_handler = f"/app/data/chrome-extensions/distinct-chrome-extension_{handler_uuid}"
        ace_ext_for_handler = f"/app/data/chrome-extensions/ace-chrome-extension_{handler_uuid}"
        if os.path.exists(distinct_ext_for_handler):
            shutil.rmtree(distinct_ext_for_handler)
        shutil.copytree("/app/distinct-chrome-extension", distinct_ext_for_handler)
        if os.path.exists(ace_ext_for_handler):
            shutil.rmtree(ace_ext_for_handler)
        shutil.copytree("/app/ace-chrome-extension", ace_ext_for_handler)

        # Configure distinct chrome extension
        with open(f"{distinct_ext_for_handler}/config/config.json", "w") as f:
            f.write(json.dumps({
                "core_endpoint": "http://distinct-core:8080",
                "handler_uuid": handler_uuid
            }))

        # Configure ace chrome extension
        with open(f"{ace_ext_for_handler}/config/config.json", "w") as f:
            f.write(json.dumps({
                "googleUsername": os.environ["GOOGLE_USERNAME"],
                "googlePassword": os.environ["GOOGLE_PASSWORD"],
                "facebookUsername": os.environ["FACEBOOK_USERNAME"],
                "facebookPassword": os.environ["FACEBOOK_PASSWORD"],
                "appleUsername": os.environ["APPLE_USERNAME"],
                "applePassword": os.environ["APPLE_PASSWORD"],
                "apple2FA": os.environ["APPLE_2FA"]
            }))

        return (
            distinct_ext_for_handler,
            ace_ext_for_handler,
            "/app/ublock-chrome-extension"
        )

    def start_proxy(self, handler_uuid):
        logger.info(f"Starting proxy with handler uuid {handler_uuid}")
        # stdout = f"/app/data/chrome-proxy/proxy-stdout_{handler_uuid}.log"
        # stderr = f"/app/data/chrome-proxy/proxy-stderr_{handler_uuid}.log"
        stream_path = f"/app/data/chrome-proxy/proxy-stream_{handler_uuid}.dump"
        hardump_path = f"/app/data/chrome-proxy/proxy-hardump_{handler_uuid}.har"

        listen_host = "127.0.0.1"
        listen_port = self.get_free_port()

        p = subprocess.Popen([
            "mitmdump",
            "--listen-host", listen_host,
            "--listen-port", str(listen_port),
            "--save-stream-file", stream_path,
            "--quiet",
            "--scripts", "/app/mitmproxy/har.py",
            "--scripts", "/app/mitmproxy/redirects.py",
            "--set", f"hardump={hardump_path}"
        ])
        self.proxies_by_handler[handler_uuid] = p

        logger.info(f"Started proxy on {listen_host}:{listen_port}")
        return (
            listen_host,
            listen_port,
            p
        )

    def stop_proxy(self, handler_uuid):
        logger.info(f"Stopping proxy with handler uuid {handler_uuid}")
        self.proxies_by_handler[handler_uuid].terminate()

    def start_browser(self, handler_uuid, config):
        """ Start new browser process for handler uuid """
        logger.info(f"Starting browser with handler uuid {handler_uuid}")
        if "initurl" in config:
            logger.info(f"Init URL: {config['initurl']}")

        # Setup chrome extensions
        exts = self.setup_chrome_extensions(handler_uuid)

        # Start proxy
        proxy_host, proxy_port, proxy = self.start_proxy(handler_uuid)

        # Start browser process
        gui_env = os.environ.copy()
        gui_env["DISPLAY"] = ":0.0"
        p = subprocess.Popen([
            "/app/distinct-chromium/chrome",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--ignore-certificate-errors",
            "--allow-running-insecure-content",
            "--disable-site-isolation-trials",
            "--disable-http2",
            f"--proxy-server={proxy_host}:{proxy_port}",
            f"--proxy-bypass-list=distinct-core",
            f"--load-extension={','.join(exts)}",
            f"--user-data-dir=/app/data/chrome-profiles/chrome-profile_{handler_uuid}",
            config["initurl"] if "initurl" in config else ""
        ], env=gui_env)
        self.browsers_by_handler[handler_uuid] = p

    def stop_browser(self, handler_uuid):
        """ Stop browser process and proxy for handler uuid """
        logger.info(f"Stopping browser with handler uuid {handler_uuid}")
        self.browsers_by_handler[handler_uuid].terminate()
        self.stop_proxy(handler_uuid)

    """ Wrappers """

    def check_browser_existence(func):
        """ Error when there is no browser for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if handler_uuid in browserapi.browsers_by_handler:
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with handler uuid {handler_uuid} does not exist")
                body = {"success": False, "error": f"Browser with handler uuid {handler_uuid} does not exist", "data": None}
                return body
        return wrapper

    def check_proxy_existence(func):
        """ Error when there is no proxy for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if handler_uuid in browserapi.proxies_by_handler:
                return func(*args, **kwargs)
            else:
                logger.error(f"Proxy with handler uuid {handler_uuid} does not exist")
                body = {"success": False, "error": f"Proxy with handler uuid {handler_uuid} does not exist", "data": None}
                return body
        return wrapper

    def check_browser_absense(func):
        """ Error when there is a browser for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if handler_uuid not in browserapi.browsers_by_handler:
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with handler uuid {handler_uuid} already exist")
                body = {"success": False, "error": f"Browser with handler uuid {handler_uuid} already exists", "data": None}
                return body
        return wrapper

    def check_browser_running(func):
        """ Error when there is no browser running for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if (
                handler_uuid in browserapi.browsers_by_handler
                and browserapi.browsers_by_handler[handler_uuid].poll() is None
            ):
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with handler uuid {handler_uuid} is not running")
                body = {"success": False, "error": f"Browser with handler uuid {handler_uuid} is not running", "data": None}
                return body
        return wrapper

    def check_browser_not_running(func):
        """ Error when there is a browser running for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if (
                (
                    # There is no browser for handler uuid
                    handler_uuid not in browserapi.browsers_by_handler
                ) or (
                    # There is a browser for handler uuid but it is not running
                    handler_uuid in browserapi.browsers_by_handler
                    and browserapi.browsers_by_handler[handler_uuid].poll() is not None
                )
            ):
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with handler uuid {handler_uuid} is still running")
                body = {"success": False, "error": f"Browser with handler uuid {handler_uuid} is still running", "data": None}
                return body
        return wrapper

    def check_proxy_not_running(func):
        """ Error when there is a proxy running for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if (
                (
                    # There is no proxy for handler uuid
                    handler_uuid not in browserapi.proxies_by_handler
                ) or (
                    # There is a proxy for handler uuid but it is not running
                    handler_uuid in browserapi.proxies_by_handler
                    and browserapi.proxies_by_handler[handler_uuid].poll() is not None
                )
            ):
                return func(*args, **kwargs)
            else:
                logger.error(f"Proxy with handler uuid {handler_uuid} is still running")
                body = {"success": False, "error": f"Proxy with handler uuid {handler_uuid} is still running", "data": None}
                return body
        return wrapper

    """ Webserver API Routes """

    # GET /api/browsers/
    def api_browsers(self):
        body = {"success": True, "error": None, "data": []}
        for uuid, process in self.browsers_by_handler.items():
            data = {
                "uuid": uuid,
                "browser": {
                    "pid": process.pid,
                    "returncode": process.poll(),
                    "args": process.args
                }
            }
            if uuid in self.proxies_by_handler:
                data["proxy"] = {
                    "pid": self.proxies_by_handler[uuid].pid,
                    "returncode": self.proxies_by_handler[uuid].poll(),
                    "args": self.proxies_by_handler[uuid].args
                }
            else:
                data["proxy"] = None
            body["data"].append(data)
        return body

    # GET /api/browsers/<handler_uuid>/
    def api_browsers_handler(self, handler_uuid):
        body = {
            "success": True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "browser": None,
                "proxy": None
            }
        }
        if handler_uuid in self.browsers_by_handler:
            body["data"]["browser"] = {
                "pid": self.browsers_by_handler[handler_uuid].pid,
                "returncode": self.browsers_by_handler[handler_uuid].poll(),
                "args": self.browsers_by_handler[handler_uuid].args
            }
        if handler_uuid in self.proxies_by_handler:
            body["data"]["proxy"] = {
                "pid": self.proxies_by_handler[handler_uuid].pid,
                "returncode": self.proxies_by_handler[handler_uuid].poll(),
                "args": self.proxies_by_handler[handler_uuid].args
            }
        return body

    # POST /api/browsers/<handler_uuid>/start
    @check_browser_absense
    def api_browsers_start(self, handler_uuid):
        config = request.get_json() if request.is_json else {}
        self.start_browser(handler_uuid, config)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /api/browsers/<handler_uuid>/stop
    @check_browser_existence
    @check_browser_running
    def api_browsers_stop(self, handler_uuid):
        self.stop_browser(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body

    # GET /api/browsers/<handler_uuid>/profile
    @check_browser_existence
    @check_browser_not_running
    def api_browsers_profile(self, handler_uuid):
        profile_path = f"/app/data/chrome-profiles/chrome-profile_{handler_uuid}"
        profile_zip_path = f"/app/data/chrome-profiles/chrome-profile_{handler_uuid}.zip"

        if os.path.isfile(profile_zip_path):
            os.remove(profile_zip_path)

        if os.path.exists(profile_path):
            shutil.make_archive(profile_path, "zip", profile_path)
            with open(profile_zip_path, "rb") as f:
                profile_zip_bytes = f.read()
                profile_zip_b64 = base64.b64encode(profile_zip_bytes).decode("utf8")
                body = {"success": True, "error": None, "data": profile_zip_b64}
                return body
        else:
            body = {"success": False, "error": f"Profile for handler uuid {handler_uuid} does not exist", "data": None}
            return body

    # GET /api/proxies/<handler_uuid>/stream
    @check_proxy_existence
    @check_proxy_not_running
    def api_proxies_stream(self, handler_uuid):
        stream_path = f"/app/data/chrome-proxy/proxy-stream_{handler_uuid}.dump"
        if os.path.exists(stream_path):
            with open(stream_path, "rb") as f:
                stream_bytes = f.read()
                stream_b64 = base64.b64encode(stream_bytes).decode("utf8")
                body = {"success": True, "error": None, "data": stream_b64}
                return body
        else:
            body = {"success": False, "error": f"Proxy stream for handler uuid {handler_uuid} does not exist", "data": None}
            return body

    # GET /api/proxies/<handler_uuid>/har
    @check_proxy_existence
    @check_proxy_not_running
    def api_proxies_har(self, handler_uuid):
        har_path = f"/app/data/chrome-proxy/proxy-hardump_{handler_uuid}.har"
        if os.path.exists(har_path):
            with open(har_path, "rb") as f:
                har_bytes = f.read()
                har_b64 = base64.b64encode(har_bytes).decode("utf8")
                body = {"success": True, "error": None, "data": har_b64}
                return body
        else:
            body = {"success": False, "error": f"Proxy har for handler uuid {handler_uuid} does not exist", "data": None}
            return body

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    browser_api = BrowserAPI()
    browser_api.start()
    browser_api.join()


if __name__ == "__main__":
    main()
