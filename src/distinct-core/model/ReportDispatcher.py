import logging
import os
import requests
import base64
import io
import pymongo
import gridfs
from threading import Thread
from functools import wraps
from flask import Flask, request, redirect, send_file, send_from_directory
from flask_cors import CORS
from bson import ObjectId
from model.ReportHandler import ReportHandler
from model.ReportHandlerStatus import ReportHandlerStatus
from model.ProxyStatus import ProxyStatus
from model.BrowserStatus import BrowserStatus

logger = logging.getLogger(__name__)

class ReportDispatcher(Thread):

    dbEndpoint = os.environ["DISTINCT_DB"]
    browserEndpoint = os.environ["DISTINCT_BROWSER_API"] \
        if os.environ["PYTHON_APP_MODE"] == "prod" else None
    appMode = os.environ["PYTHON_APP_MODE"]

    def __init__(self):
        logger.info("Initializing report dispatcher thread")
        super(ReportDispatcher, self).__init__()

        # Init the database
        self.db = self.connect_db(self.dbEndpoint)
        self.fs = gridfs.GridFS(self.db["distinct"])

        self.handlers = {}
        self.restore_handlers()

        self.app = Flask(__name__, static_folder="../gui/dist", static_url_path="/static")
        self.app.url_map.strict_slashes = False # allow trailing slashes
        CORS(self.app, resources={r"/api/*": {"origins": "*"}}) # enable CORS
        self.register_routes()

    def run(self):
        logger.info("Starting report dispatcher thread")

        listen_host = "0.0.0.0"
        listen_port = 9080

        logger.info(f"Starting webserver on {listen_host}:{listen_port}")
        self.app.run(host=listen_host, port=listen_port)

    def register_routes(self):
        logger.info("Registering routes for the report dispatcher's webserver")

        # Frontend
        self.app.add_url_rule("/", view_func=self.frontend, methods=["GET"])
        self.app.add_url_rule("/paper.pdf", view_func=self.paper, methods=["GET"])
        self.app.add_url_rule("/paper.bib", view_func=self.bib, methods=["GET"])

        # Pocs
        self.app.add_url_rule("/pocs/<handler_uuid>", view_func=self.send_poc, methods=["GET"])

        # Report handlers
        if self.prod(): self.app.add_url_rule("/api/handlers", view_func=self.api_handlers, methods=["GET", "POST"])
        else: self.app.add_url_rule("/api/handlers", view_func=self.api_handlers, methods=["GET"])
        if self.prod(): self.app.add_url_rule("/api/handlers/<handler_uuid>/stop", view_func=self.api_handlers_stop, methods=["POST"])
        if self.prod(): self.app.add_url_rule("/api/handlers/<handler_uuid>/remove", view_func=self.api_handlers_remove, methods=["POST"])

        # Reports
        if self.prod(): self.app.add_url_rule("/api/handlers/<handler_uuid>/dispatch", view_func=self.api_handlers_dispatch, methods=["POST"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/reports", view_func=self.api_handlers_reports, methods=["GET"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/svg", view_func=self.api_handlers_svg, methods=["GET"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/statements", view_func=self.api_handlers_statements, methods=["GET"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/poc", view_func=self.api_handlers_poc, methods=["GET"])

        # Browsers
        if self.prod(): self.app.add_url_rule("/api/browsers/<handler_uuid>/start", view_func=self.api_browsers_start, methods=["POST"])
        if self.prod(): self.app.add_url_rule("/api/browsers/<handler_uuid>/stop", view_func=self.api_browsers_stop, methods=["POST"])
        if self.prod(): self.app.add_url_rule("/api/browsers/<handler_uuid>/profile", view_func=self.api_browsers_profile, methods=["GET"])

        # Proxies
        if self.prod(): self.app.add_url_rule("/api/proxies/<handler_uuid>/stream", view_func=self.api_proxies_stream, methods=["GET"])
        if self.prod(): self.app.add_url_rule("/api/proxies/<handler_uuid>/har", view_func=self.api_proxies_har, methods=["GET"])

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

    def prod(self):
        return self.appMode == "prod"

    def restore_handlers(self):
        logger.info("Restoring handlers")
        for d in self.db["distinct"]["handlers"].find():
            self.restore_report_handler(d["handler"]["uuid"])

    def restore_report_handler(self, handler_uuid):
        logger.info(f"Restoring report handler with uuid: {handler_uuid}")
        d = self.db["distinct"]["handlers"].find_one({"handler_uuid": handler_uuid})
        report_handler = ReportHandler(self, uuid=d["handler"]["uuid"])
        if ReportHandlerStatus(d["handler"]["status"]) == ReportHandlerStatus.STOPPED:
            report_handler.should_stop = True
        report_handler.start()
        self.handlers[report_handler.uuid] = report_handler
        return report_handler

    def new_report_handler(self, config):
        logger.info("Creating new report handler")
        report_handler = ReportHandler(self, config=config)
        report_handler.start()
        self.handlers[report_handler.uuid] = report_handler
        return report_handler

    def stop_report_handler(self, handler_uuid):
        logger.info(f"Stopping report handler with uuid: {handler_uuid}")
        if self.handlers[handler_uuid].is_alive():
            self.handlers[handler_uuid].stop()

    def remove_report_handler(self, handler_uuid):
        logger.info(f"Removing report handler with uuid: {handler_uuid}")
        if self.handlers[handler_uuid].is_alive():
            self.handlers[handler_uuid].stop()
        del self.handlers[handler_uuid]
        self.db["distinct"]["handlers"].delete_many({"handler_uuid": handler_uuid})
        self.db["distinct"]["reports"].delete_many({"handler_uuid": handler_uuid})
        self.db["distinct"]["statements"].delete_many({"handler_uuid": handler_uuid})
        self.db["distinct"]["proxies"].delete_many({"handler_uuid": handler_uuid})
        self.db["distinct"]["browsers"].delete_many({"handler_uuid": handler_uuid})

    def pass_report_to_handler(self, report, handler_uuid):
        # report = {"report": {"key": str, "val": any}}
        if handler_uuid in self.handlers:
            self.handlers[handler_uuid].queue_report(report)
            return True
        else:
            logger.error(f"Failed to dispatch report to report handler with uuid"
            f" {handler_uuid} because the report handler does not exist")
            return False

    def deploy_poc(self, handler_uuid, poc):
        logger.info(f"Deploying poc for handler with uuid: {handler_uuid}")
        filename = f"/app/data/pocs/{handler_uuid}.html"
        with open(filename, "w+") as f:
            f.write(poc)
        return f"/pocs/{handler_uuid}.html"

    """ Wrappers """

    def check_handler_existence(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dispatcher = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if handler_uuid in dispatcher.handlers:
                return func(*args, **kwargs)
            else:
                logger.error(f"Report handler with uuid {handler_uuid} does not exist")
                body = {"success": False, "error": "Report handler does not exist", "data": None}
                return body
        return wrapper

    """ GUI Routes """

    # GET /
    def frontend(self):
        return self.app.send_static_file("index.html")

    # GET /paper.pdf
    def paper(self):
        return send_from_directory("../", "paper.pdf", as_attachment=True)

    # GET /paper.bib
    def bib(self):
        return send_from_directory("../", "paper.bib", as_attachment=False)

    # GET /pocs/<handler_uuid>
    def send_poc(self, handler_uuid):
        return send_from_directory("/app/data/pocs", handler_uuid)

    """ API Routes: Handlers """

    # GET|POST /api/handlers
    def api_handlers(self):
        # GET /api/handlers
        if request.method == "GET":
            body = {"success":True, "error": None, "data": []}

            for uuid, handler in self.handlers.items():
                # Get browser and proxy for uuid
                r_browser = self.get_browsers_by_handler(uuid)
                browser_for_uuid = r_browser["data"]["browser"] or None
                proxy_for_uuid = r_browser["data"]["proxy"] or None

                body["data"].append({
                    "uuid": uuid,
                    "running": handler.is_alive(),
                    "starttime": handler.starttime,
                    "reportsCount": handler.counter,
                    "queueSize": handler.queue.qsize(),
                    "browser": browser_for_uuid,
                    "proxy": proxy_for_uuid
                })
            return body

        # POST /api/handlers [preloadurl=<url>]
        elif request.method == "POST":
            config = request.get_json() if request.is_json else {}
            report_handler = self.new_report_handler(config)
            r_browsers = self.get_browsers_by_handler(report_handler.uuid)

            # Get browser list for uuid
            browser_for_uuid = None # {"pid": ..., "returncode": ..., "args": ...}
            proxy_for_uuid = None # {"pid": ..., "returncode": ..., "args": ...}
            if r_browsers["success"] == True:
                browser_for_uuid = r_browsers["data"]["browser"]
                proxy_for_uuid = r_browsers["data"]["proxy"]

            body = {
                "success":True,
                "error": None,
                "data": {
                    "uuid": report_handler.uuid,
                    "running": report_handler.is_alive(),
                    "starttime": report_handler.starttime,
                    "reportsCount": report_handler.counter,
                    "queueSize": report_handler.queue.qsize(),
                    "browser": browser_for_uuid,
                    "proxy": proxy_for_uuid
                }
            }
            return body

    # POST /api/handlers/<handler_uuid>/stop
    @check_handler_existence
    def api_handlers_stop(self, handler_uuid):
        self.stop_report_handler(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /api/handlers/<handler_uuid>/remove
    @check_handler_existence
    def api_handlers_remove(self, handler_uuid):
        self.remove_report_handler(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /api/handlers/<handler_uuid>/dispatch
    @check_handler_existence
    def api_handlers_dispatch(self, handler_uuid):
        report = request.get_json() # {"report": {"key": str, "val": any}}
        if (
            report
            and "report" in report
            and "key" in report["report"]
            and "val" in report["report"]
        ):
            self.pass_report_to_handler(report, handler_uuid)
            body = {"success": True, "error": None, "data": None}
            return body
        else:
            body = {"success": False, "error": "Invalid report format", "data": None}
            return body

    # GET /api/handlers/<handler_uuid>/reports
    @check_handler_existence
    def api_handlers_reports(self, handler_uuid):
        body = {
            "success":True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "reports": self.handlers[handler_uuid].ctx.reports
            }
        }
        return body

    # GET /api/handlers/<handler_uuid>/svg
    @check_handler_existence
    def api_handlers_svg(self, handler_uuid):
        body = {
            "success":True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "svg": self.handlers[handler_uuid].ctx.sequencediagram.svg()
            }
        }
        return body

    # GET /api/handlers/<handler_uuid>/statements
    @check_handler_existence
    def api_handlers_statements(self, handler_uuid):
        body = {
            "success":True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "statements": self.handlers[handler_uuid].ctx.statements
            }
        }
        return body

    # GET /api/handlers/<handler_uuid>/poc
    @check_handler_existence
    def api_handlers_poc(self, handler_uuid):
        success, val = self.handlers[handler_uuid].ctx.poc.generate_poc()
        poc_url = self.deploy_poc(handler_uuid, val)
        if success:
            body = {
                "success": True,
                "error": None,
                "data": {
                    "uuid": handler_uuid,
                    "poc_url": poc_url,
                    "poc": val
                }
            }
        else:
            body = {
                "success": False,
                "error": val,
                "data": None
            }
        return body

    """ API Routes: Browsers """

    # POST /api/browsers/<handler_uuid>/start
    @check_handler_existence
    def api_browsers_start(self, handler_uuid):
        config = self.handlers[handler_uuid].config
        r = self.start_browser(handler_uuid, config)
        return r

    # POST /api/browsers/<handler_uuid>/stop
    @check_handler_existence
    def api_browsers_stop(self, handler_uuid):
        r = self.stop_browser(handler_uuid)
        return r

    # GET /api/browsers/<handler_uuid>/profile
    @check_handler_existence
    def api_browsers_profile(self, handler_uuid):
        r = self.get_profile_by_handler(handler_uuid)
        if r["success"] == True:
            profile_zip = base64.b64decode(r["data"])
            return send_file(
                io.BytesIO(profile_zip),
                download_name=f"chrome-profile_{handler_uuid}.zip",
                as_attachment=True,
                mimetype="application/zip"
            )
        else:
            return r

    # GET /api/proxies/<handler_uuid>/stream
    @check_handler_existence
    def api_proxies_stream(self, handler_uuid):
        r = self.get_stream_by_handler(handler_uuid)
        if r["success"] == True:
            stream = base64.b64decode(r["data"])
            return send_file(
                io.BytesIO(stream),
                download_name=f"proxy-stream_{handler_uuid}.dump",
                as_attachment=True,
                mimetype="application/octet-stream"
            )
        else:
            return r

    # GET /api/proxies/<handler_uuid>/har
    @check_handler_existence
    def api_proxies_har(self, handler_uuid):
        r = self.get_har_by_handler(handler_uuid)
        if r["success"] == True:
            har = base64.b64decode(r["data"])
            return send_file(
                io.BytesIO(har),
                download_name=f"proxy-hardump_{handler_uuid}.har",
                as_attachment=True,
                mimetype="application/octet-stream"
            )
        else:
            return r

    """ Browser Connectors """

    def start_browser(self, handler_uuid, config):
        r = requests.post(f"{self.browserEndpoint}/api/browsers/{handler_uuid}/start", json=config)
        return r.json()

    def stop_browser(self, handler_uuid):
        r = requests.post(f"{self.browserEndpoint}/api/browsers/{handler_uuid}/stop")
        return r.json()

    def get_browsers_by_handler(self, handler_uuid):
        body = {
            "success": True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "browser": None,
                "proxy": None
            }
        }
        browser = self.db["distinct"]["browsers"].find_one({"handler_uuid": handler_uuid})
        proxy = self.db["distinct"]["proxies"].find_one({"handler_uuid": handler_uuid})
        if browser:
            body["data"]["browser"] = {
                "pid": browser["browser"]["pid"],
                "returncode": browser["browser"]["returncode"],
                "args": browser["browser"]["args"]
            }
        if proxy:
            body["data"]["proxy"] = {
                "pid": proxy["proxy"]["pid"],
                "returncode": proxy["proxy"]["returncode"],
                "args": proxy["proxy"]["args"]
            }
        return body

    def get_profile_by_handler(self, handler_uuid):
        d = self.db["distinct"]["browsers"].find_one({"handler_uuid": handler_uuid})
        if d is None:
            return {"success": False, "error": f"Browser for handler uuid {handler_uuid} was not yet started", "data": None}
        bstat = BrowserStatus(d["browser"]["status"])
        profile_fs = d["browser"]["profile"]
        if profile_fs:
            profile_obj = ObjectId(profile_fs)
            profile = self.fs.get(profile_obj).read().decode("utf8")
            return {"success": True, "error": None, "data": profile}
        elif profile_fs is None and bstat == BrowserStatus.RUNNING:
            return {"success": False, "error": f"Browser for handler uuid {handler_uuid} is still running", "data": None}
        else:
            return {"success": False, "error": f"Profile for handler uuid {handler_uuid} does not exist", "data": None}

    def get_stream_by_handler(self, handler_uuid):
        d = self.db["distinct"]["proxies"].find_one({"handler_uuid": handler_uuid})
        if d is None:
            return {"success": False, "error": f"Browser for handler uuid {handler_uuid} was not yet started", "data": None}
        pstat = ProxyStatus(d["proxy"]["status"])
        stream_fs = d["proxy"]["stream"]
        if stream_fs:
            stream_obj = ObjectId(stream_fs)
            stream = self.fs.get(stream_obj).read().decode("utf8")
            return {"success": True, "error": None, "data": stream}
        elif stream_fs is None and pstat == ProxyStatus.RUNNING:
            return {"success": False, "error": f"Proxy for handler uuid {handler_uuid} is still running", "data": None}
        else:
            return {"success": False, "error": f"Proxy stream for handler uuid {handler_uuid} does not exist", "data": None}

    def get_har_by_handler(self, handler_uuid):
        d = self.db["distinct"]["proxies"].find_one({"handler_uuid": handler_uuid})
        if d is None:
            return {"success": False, "error": f"Browser for handler uuid {handler_uuid} was not yet started", "data": None}
        pstat = ProxyStatus(d["proxy"]["status"])
        hardump_fs = d["proxy"]["hardump"]
        if hardump_fs:
            hardump_obj = ObjectId(hardump_fs)
            hardump = self.fs.get(hardump_obj).read().decode("utf8")
            return {"success": True, "error": None, "data": hardump}
        elif hardump_fs is None and pstat == ProxyStatus.RUNNING:
            return {"success": False, "error": f"Proxy for handler uuid {handler_uuid} is still running", "data": None}
        else:
            return {"success": False, "error": f"Proxy har for handler uuid {handler_uuid} does not exist", "data": None}
