#!/usr/bin/env python3

import logging
import sys
import subprocess
import os
import shutil
import json
from threading import Thread
from functools import wraps
from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)

class BrowserAPI(Thread):

    def __init__(self):
        logger.info("Initializing browser api thread")
        super(BrowserAPI, self).__init__()
        self.daemon = True

        self.app = Flask(__name__)
        self.app.url_map.strict_slashes = False # allow trailing slashes
        CORS(self.app, resources={r"/api/*": {"origins": "*"}}) # enable CORS
        self.register_routes()

        self.browsers_by_handler = {} # {handler_uuid: [Pprocess, ...]}

    def run(self):
        logger.info("Starting browser api thread")

        listen_host = "0.0.0.0"
        listen_port = 80

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
            "/api/browsers/<handler_uuid>/start", view_func=self.api_browsers_handler_start, methods=["POST"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>/stop", view_func=self.api_browsers_handler_stop, methods=["POST"]
        )

    """ Routines """

    def start_browser(self, handler_uuid):
        """ Start new browser process for handler uuid """
        logger.info(f"Starting browser with handler uuid {handler_uuid}")

        # Setup chrome extensions for handler
        distinct_ext_for_handler = f"/app/chrome-extensions/distinct-chrome-extension-{handler_uuid}"
        ace_ext_for_handler = f"/app/chrome-extensions/ace-chrome-extension-{handler_uuid}"
        if os.path.exists(distinct_ext_for_handler):
            shutil.rmtree(distinct_ext_for_handler)
        shutil.copytree("/app/distinct-chrome-extension", distinct_ext_for_handler)
        if os.path.exists(ace_ext_for_handler):
            shutil.rmtree(ace_ext_for_handler)
        shutil.copytree("/app/ace-chrome-extension", ace_ext_for_handler)

        # Configure chrome extension
        with open(f"{distinct_ext_for_handler}/config/config.json", "w") as f:
            f.write(json.dumps({
                "core_endpoint": "http://distinct-core",
                "handler_uuid": handler_uuid
            }))

        # Start browser process
        gui_env = os.environ.copy()
        gui_env["DISPLAY"] = ":0.0"
        p = subprocess.Popen([
            "/chromium/latest/chrome",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--ignore-certificate-errors",
            "--allow-running-insecure-content",
            "--disable-site-isolation-trials",
            f"--load-extension={distinct_ext_for_handler},{ace_ext_for_handler}",
            f"--user-data-dir=/app/chrome-profiles/chrome-profile-{handler_uuid}",
        ], env=gui_env)

        # Save browser process in list of browsers
        if handler_uuid not in self.browsers_by_handler:
            self.browsers_by_handler[handler_uuid] = [p]
        else:
            self.browsers_by_handler[handler_uuid].append(p)

    def stop_browser(self, handler_uuid):
        """ Stop browser process for handler uuid """
        logger.info(f"Stopping browser with handler uuid {handler_uuid}")
        self.browsers_by_handler[handler_uuid][-1].terminate()

        # Cleanup chrome extensions for handler
        distinct_ext_for_handler = f"/app/chrome-extensions/distinct-chrome-extension-{handler_uuid}"
        ace_ext_for_handler = f"/app/chrome-extensions/ace-chrome-extension-{handler_uuid}"
        if os.path.exists(distinct_ext_for_handler):
            shutil.rmtree(distinct_ext_for_handler)
        if os.path.exists(ace_ext_for_handler):
            shutil.rmtree(ace_ext_for_handler)

    """ Wrappers """

    def check_browser_existence(func):
        """ Error when there is not a single browser for handler uuid """
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

    def check_browser_running(func):
        """ Error when there is no browser running for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if (
                handler_uuid in browserapi.browsers_by_handler
                and browserapi.browsers_by_handler[handler_uuid][-1]
                and browserapi.browsers_by_handler[handler_uuid][-1].poll() is None
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
                    and browserapi.browsers_by_handler[handler_uuid][-1]
                    and browserapi.browsers_by_handler[handler_uuid][-1].poll() is not None
                )
            ):
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with handler uuid {handler_uuid} is already running")
                body = {"success": False, "error": f"Browser with handler uuid {handler_uuid} is already running", "data": None}
                return body
        return wrapper

    """ Webserver API Routes """

    # GET /api/browsers/
    def api_browsers(self):
        body = {"success": True, "error": None, "data": []}
        for uuid, processes in self.browsers_by_handler.items():
            data = {"uuid": uuid, "browsers": []}
            for process in processes:
                data["browsers"].append({"pid": process.pid, "returncode": process.poll()})
            body["data"].append(data)
        return body

    # GET /api/browsers/<handler_uuid>/
    def api_browsers_handler(self, handler_uuid):
        body = {
            "success": True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "browsers": []
            }
        }
        if handler_uuid in self.browsers_by_handler:
            for process in self.browsers_by_handler[handler_uuid]:
                body["data"]["browsers"].append({"pid": process.pid, "returncode": process.poll()})
        return body

    # POST /api/browsers/<handler_uuid>/start
    @check_browser_not_running
    def api_browsers_handler_start(self, handler_uuid):
        self.start_browser(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /api/browsers/<handler_uuid>/stop
    @check_browser_existence
    @check_browser_running
    def api_browsers_handler_stop(self, handler_uuid):
        self.stop_browser(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    browser_api = BrowserAPI()
    browser_api.start()
    browser_api.join()


if __name__ == "__main__":
    main()
