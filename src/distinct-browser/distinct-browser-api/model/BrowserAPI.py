import logging
import subprocess
import os
import shutil
import json
import base64
import pymongo
import gridfs
import time
from threading import Thread
from functools import wraps
from socket import socket
from flask import Flask, request
from flask_cors import CORS
from model.ProcessCleaner import ProcessCleaner
from model.BrowserStatus import BrowserStatus
from model.ProxyStatus import ProxyStatus

logger = logging.getLogger(__name__)

class BrowserAPI(Thread):

    dbEndpoint = os.environ["DISTINCT_DB"]
    coreEndpoint = os.environ["DISTINCT_CORE"]

    def __init__(self):
        logger.info("Initializing browser api thread")
        super(BrowserAPI, self).__init__()

        # Init the database
        self.db = self.connect_db(self.dbEndpoint)
        self.fs = gridfs.GridFS(self.db["distinct"])

        self.app = Flask(__name__)
        self.app.url_map.strict_slashes = False # allow trailing slashes
        CORS(self.app, resources={r"/api/*": {"origins": "*"}}) # enable CORS
        self.register_routes()

        self.browsers_by_handler = {} # {handler_uuid: Pprocess, ...}
        self.proxies_by_handler = {} # {handler_uuid: Pprocess, ...}

        self.process_cleaner = ProcessCleaner(self)
        self.process_cleaner.start()

    def run(self):
        logger.info("Starting browser api thread")

        listen_host = "0.0.0.0"
        listen_port = 9081

        logger.info(f"Starting webserver on {listen_host}:{listen_port}")
        self.app.run(host=listen_host, port=listen_port)

    def register_routes(self):
        logger.info("Registering routes for the browser api's webserver")

        self.app.add_url_rule("/api/browsers/<handler_uuid>/start", view_func=self.api_browsers_start, methods=["POST"])
        self.app.add_url_rule("/api/browsers/<handler_uuid>/stop", view_func=self.api_browsers_stop, methods=["POST"])

    def process_poller():
        pass

    """ Routines """

    @staticmethod
    def connect_db(endpoint):
        logger.info(f"Connecting to the database: {endpoint}")
        db = pymongo.MongoClient(endpoint)
        try:
            db.admin.command("ping")
            logger.info("Successfully connected to the database")
            return db
        except pymongo.errors.ConnectionFailure:
            logger.error("Failed to connect to the database. Not reachable. Quitting...")
            exit(-1)

    @staticmethod
    def get_free_port():
        with socket() as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def setup_chrome_extensions(self, handler_uuid):
        """ Setup chrome extensions for handler """
        logger.info(f"Setting up chrome extensions for handler uuid {handler_uuid}")
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
                "core_endpoint": coreEndpoint,
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

    def destroy_chrome_extensions(self, handler_uuid):
        """ Destroy chrome extensions for handler """
        logger.info(f"Destroying chrome extensions for handler uuid {handler_uuid}")
        distinct_ext_for_handler = f"/app/data/chrome-extensions/distinct-chrome-extension_{handler_uuid}"
        ace_ext_for_handler = f"/app/data/chrome-extensions/ace-chrome-extension_{handler_uuid}"
        if os.path.exists(distinct_ext_for_handler):
            shutil.rmtree(distinct_ext_for_handler)
        if os.path.exists(ace_ext_for_handler):
            shutil.rmtree(ace_ext_for_handler)

    def start_proxy(self, handler_uuid):
        logger.info(f"Starting proxy with handler uuid {handler_uuid}")
        # stdout = f"/app/data/chrome-proxy/proxy-stdout_{handler_uuid}.log"
        # stderr = f"/app/data/chrome-proxy/proxy-stderr_{handler_uuid}.log"
        stream_path = f"/app/data/chrome-proxy/proxy-stream_{handler_uuid}.dump"
        hardump_path = f"/app/data/chrome-proxy/proxy-hardump_{handler_uuid}.har"

        listen_host = "127.0.0.1"
        listen_port = self.get_free_port()

        p = subprocess.Popen(
            [
                "mitmdump",
                "--listen-host", listen_host,
                "--listen-port", str(listen_port),
                "--save-stream-file", stream_path,
                "--quiet",
                "--scripts", "/app/mitmproxy/har.py",
                "--scripts", "/app/mitmproxy/redirects.py",
                "--set", f"hardump={hardump_path}"
            ],
            stdout=subprocess.DEVNULL if logger.level > logging.DEBUG else None,
            stderr=subprocess.DEVNULL if logger.level > logging.DEBUG else None
        )
        self.proxies_by_handler[handler_uuid] = p
        self.db["distinct"]["proxies"].insert_one({
            "handler_uuid": handler_uuid,
            "proxy": {
                "pid": p.pid,
                "args": p.args,
                "returncode": p.poll(),
                "starttime": str(int(time.time())),
                "endtime": None,
                "status": ProxyStatus.RUNNING.value,
                "listen_host": listen_host,
                "listen_port": listen_port,
                "stream_path": stream_path,
                "stream": None,
                "hardump_path": hardump_path,
                "hardump": None
            }
        })

        logger.info(f"Started proxy on {listen_host}:{listen_port}")
        return (
            listen_host,
            listen_port,
            p
        )

    def stop_proxy(self, handler_uuid, expected_quit=True):
        logger.info(f"Stopping proxy with handler uuid {handler_uuid}")
        self.proxies_by_handler[handler_uuid].terminate()

        # Wait for STREAM and HAR files to be created
        stream_path = f"/app/data/chrome-proxy/proxy-stream_{handler_uuid}.dump"
        har_path = f"/app/data/chrome-proxy/proxy-hardump_{handler_uuid}.har"
        poll_int = 0.5 # seconds
        sleep_max = 30 # seconds
        sleep_ctr = 0
        while not os.path.exists(stream_path) or not os.path.exists(har_path):
            time.sleep(0.5)
            sleep_ctr += 1
            if sleep_ctr > (1 / poll_int) * sleep_max: break

        # Encode the STREAM file
        stream_b64 = None
        if os.path.exists(stream_path):
            with open(stream_path, "rb") as f:
                stream_bytes = f.read()
                stream_b64 = base64.b64encode(stream_bytes)

        # Encode the HAR file
        har_b64 = None
        if os.path.exists(har_path):
            with open(har_path, "rb") as f:
                har_bytes = f.read()
                har_b64 = base64.b64encode(har_bytes)

        # Cleanup STREAM and HAR
        if os.path.isfile(stream_path):
            os.remove(stream_path)
        if os.path.isfile(har_path):
            os.remove(har_path)

        # Update proxy in database
        if stream_b64:
            stream_fs = self.fs.put(stream_b64)
        else:
            stream_fs = None
        if har_b64:
            har_fs = self.fs.put(har_b64)
        else:
            har_fs = None
        self.db["distinct"]["proxies"].update_one(
            {"handler_uuid": handler_uuid},
            {"$set": {
                "proxy.returncode": self.proxies_by_handler[handler_uuid].poll(),
                "proxy.status": ProxyStatus.STOPPED.value,
                "proxy.endtime": str(int(time.time())),
                "proxy.stream": str(stream_fs) if stream_fs else None,
                "proxy.hardump": str(har_fs) if har_fs else None
            }}
        )
        if expected_quit:
            del self.proxies_by_handler[handler_uuid]

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
        chrome_profile_path = f"/app/data/chrome-profiles/chrome-profile_{handler_uuid}"
        p = subprocess.Popen(
            [
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
                f"--user-data-dir={chrome_profile_path}",
                config["initurl"] if "initurl" in config else ""
            ],
            env=gui_env,
            stdout=subprocess.DEVNULL if logger.level > logging.DEBUG else None,
            stderr=subprocess.DEVNULL if logger.level > logging.DEBUG else None
        )
        self.browsers_by_handler[handler_uuid] = p
        self.db["distinct"]["browsers"].insert_one({
            "handler_uuid": handler_uuid,
            "browser": {
                "pid": p.pid,
                "args": p.args,
                "returncode": p.poll(),
                "starttime": str(int(time.time())),
                "endtime": None,
                "status": BrowserStatus.RUNNING.value,
                "initurl": config["initurl"] if "initurl" in config else None,
                "profile_path": chrome_profile_path,
                "profile": None,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
                "proxy_pid": proxy.pid
            }
        })

    def stop_browser(self, handler_uuid, expected_quit=True):
        """ Stop browser process and proxy for handler uuid """
        logger.info(f"Stopping browser with handler uuid {handler_uuid}")
        if expected_quit:
            self.browsers_by_handler[handler_uuid].terminate()
            self.stop_proxy(handler_uuid)
        self.destroy_chrome_extensions(handler_uuid) # cleanup

        # Encode the profile in zip
        profile_zip_b64 = None
        profile_path = f"/app/data/chrome-profiles/chrome-profile_{handler_uuid}"
        profile_zip_path = f"/app/data/chrome-profiles/chrome-profile_{handler_uuid}.zip"
        if os.path.isfile(profile_zip_path):
            os.remove(profile_zip_path)
        if os.path.exists(profile_path):
            shutil.make_archive(profile_path, "zip", profile_path)
            with open(profile_zip_path, "rb") as f:
                profile_zip_bytes = f.read()
                profile_zip_b64 = base64.b64encode(profile_zip_bytes)

        # Cleanup profile
        if os.path.isfile(profile_zip_path):
            os.remove(profile_zip_path)
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)

        # Update browser in database
        if profile_zip_b64:
            profile_fs = self.fs.put(profile_zip_b64)
        else:
            profile_fs = None
        self.db["distinct"]["browsers"].update_one(
            {"handler_uuid": handler_uuid},
            {"$set": {
                "browser.returncode": self.browsers_by_handler[handler_uuid].poll(),
                "browser.status": BrowserStatus.STOPPED.value,
                "browser.endtime": str(int(time.time())),
                "browser.profile": str(profile_fs) if profile_fs else None
            }}
        )
        if expected_quit:
            del self.browsers_by_handler[handler_uuid]

    """ Wrappers """

    def check_browser_absense(func):
        """ Error when there is a browser process or instance for handler uuid """
        @wraps(func)
        def wrapper(*args, **kwargs):
            browserapi = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if (
                handler_uuid not in browserapi.browsers_by_handler
                and browserapi.db["distinct"]["browsers"].find_one({"handler_uuid": handler_uuid}) is None
            ):
                return func(*args, **kwargs)
            else:
                logger.error(f"Browser with handler uuid {handler_uuid} already exist")
                body = {"success": False, "error": f"Browser with handler uuid {handler_uuid} already exists", "data": None}
                return body
        return wrapper

    def check_browser_running(func):
        """ Error when there is no browser process running for handler uuid """
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
                logger.error(f"Browser process with handler uuid {handler_uuid} is not running")
                body = {"success": False, "error": f"Browser process with handler uuid {handler_uuid} is not running", "data": None}
                return body
        return wrapper

    """ Webserver API Routes """

    # POST /api/browsers/<handler_uuid>/start
    @check_browser_absense
    def api_browsers_start(self, handler_uuid):
        config = request.get_json() if request.is_json else {}
        self.start_browser(handler_uuid, config)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /api/browsers/<handler_uuid>/stop
    @check_browser_running
    def api_browsers_stop(self, handler_uuid):
        self.stop_browser(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body
