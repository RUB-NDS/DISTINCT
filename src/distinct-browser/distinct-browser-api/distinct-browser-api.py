#!/usr/bin/env python3

import logging
import sys
import subprocess
import os
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

        self.browsers = {} # {handler_uuid: Pprocess}

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
            "/api/browsers/<handler_uuid>", view_func=self.api_info_browsers, methods=["GET"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>/start", view_func=self.api_start_browsers, methods=["POST"]
        )
        self.app.add_url_rule(
            "/api/browsers/<handler_uuid>/stop", view_func=self.api_stop_browsers, methods=["POST"]
        )

    """ Routines """

    def start_browser(self, handler_uuid):
        logger.info(f"Starting browser with uuid {handler_uuid}")

        # TODO: Setup distinct chrome extension with handler uuid

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
            "--load-extension=/app/distinct-chrome-extension,ace-chrome-extension",
            "--user-data-dir=/tmp/foo1"
        ], env=gui_env)
        self.browsers[handler_uuid] = p

    def stop_browser(self, handler_uuid):
        logger.info(f"Stopping browser with uuid {handler_uuid}")
        self.browsers[handler_uuid].terminate()

    """ Wrappers """
    def check_browser_existence(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if handler_uuid in browserapi.browsers:
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with uuid {handler_uuid} does not exist")
                body = {"success": False, "error": "Browser does not exist", "data": None}
                return body
        return wrapper

    """ Webserver API Routes """

    # GET /api/browsers/
    def api_browsers(self):
        body = {"success": True, "error": None, "data": []}
        for uuid, process in self.browsers.items():
            body["data"].append({"uuid": uuid, "pid": process.pid, "returncode": process.poll()})
        return body

    # GET /api/browsers/<handler_uuid>/
    @check_browser_existence
    def api_info_browsers(self, handler_uuid):
        body = {
            "success": True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "pid": self.browsers[handler_uuid].pid,
                "returncode": self.browsers[handler_uuid].poll()
            }
        }
        return body

    # POST /api/browsers/<handler_uuid>/start
    def api_start_browsers(self, handler_uuid):
        self.start_browser(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /api/browsers/<handler_uuid>/stop
    @check_browser_existence
    def api_stop_browsers(self, handler_uuid):
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
