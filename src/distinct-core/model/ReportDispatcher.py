import logging
import requests
from threading import Thread
from functools import wraps
from flask import Flask, request, redirect
from flask_cors import CORS
from model.ReportHandler import ReportHandler

logger = logging.getLogger(__name__)

class ReportDispatcher(Thread):

    def __init__(self):
        logger.info("Initializing report dispatcher thread")
        super(ReportDispatcher, self).__init__()
        self.daemon = True

        self.handlers = {}
        self.app = Flask(__name__, static_folder="../distinct-gui/dist", static_url_path="/static")
        self.app.url_map.strict_slashes = False # allow trailing slashes
        CORS(self.app, resources={r"/api/*": {"origins": "*"}}) # enable CORS
        self.register_routes()

    def run(self):
        logger.info("Starting report dispatcher thread")

        listen_host = "0.0.0.0"
        listen_port = 80

        logger.info(f"Starting webserver on {listen_host}:{listen_port}")
        self.app.run(host=listen_host, port=listen_port)

    def register_routes(self):
        logger.info("Registering routes for the report dispatcher's webserver")

        # Frontend
        self.app.add_url_rule("/", view_func=self.index, methods=["GET"])
        self.app.add_url_rule("/app", view_func=self.frontend, methods=["GET"], defaults={"path": ""})
        self.app.add_url_rule("/app/<path:path>", view_func=self.frontend, methods=["GET"])

        # Report handlers
        self.app.add_url_rule("/api/handlers", view_func=self.api_handlers, methods=["GET", "POST"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/stop", view_func=self.api_handlers_stop, methods=["POST"])

        # Reports
        self.app.add_url_rule("/api/handlers/<handler_uuid>/dispatch", view_func=self.api_handlers_dispatch, methods=["POST"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/reports", view_func=self.api_handlers_reports, methods=["GET"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/svg", view_func=self.api_handlers_svg, methods=["GET"])

        # Browsers
        self.app.add_url_rule("/api/browsers/<handler_uuid>/start", view_func=self.api_browsers_start, methods=["POST"])
        self.app.add_url_rule("/api/browsers/<handler_uuid>/stop", view_func=self.api_browsers_stop, methods=["POST"])

    """ Routines """

    def new_report_handler(self):
        report_handler = ReportHandler(self)
        report_handler.start()
        self.handlers[report_handler.uuid] = report_handler
        return report_handler

    def stop_report_handler(self, handler_uuid):
        if self.handlers[handler_uuid].is_alive():
            self.handlers[handler_uuid].stop()

    def pass_report_to_handler(self, report, handler_uuid):
        # report = {"report": {"key": str, "val": any}}
        if handler_uuid in self.handlers:
            self.handlers[handler_uuid].queue_report(report)
            return True
        else:
            logger.error(f"Failed to dispatch report to report handler with uuid"
            f" {handler_uuid} because the report handler does not exist")
            return False

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
    def index(self):
        return redirect("/app", 302)

    # GET /app
    # GET /app/<path:path>
    def frontend(self, path):
        return self.app.send_static_file("index.html")

    """ API Routes """

    # GET|POST /api/handlers
    def api_handlers(self):
        # GET /api/handlers
        if request.method == "GET":
            body = {"success":True, "error": None, "data": []}
            r_browsers = self.get_browsers()

            for uuid, handler in self.handlers.items():
                # Get browser and proxy for uuid
                browser_for_uuid = None # {"pid": ..., "returncode": ..., "args": ...}
                proxy_for_uuid = None # {"pid": ..., "returncode": ..., "args": ...}
                if r_browsers["success"] == True:
                    for entry in r_browsers["data"]:
                        if entry["uuid"] == uuid:
                            browser_for_uuid = entry["browser"]
                            proxy_for_uuid = entry["proxy"]

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

        # POST /api/handlers
        elif request.method == "POST":
            report_handler = self.new_report_handler()
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

    # POST /api/browsers/<handler_uuid>/start
    def api_browsers_start(self, handler_uuid):
        r = self.start_browser(handler_uuid)
        return r

    # POST /api/browsers/<handler_uuid>/stop
    def api_browsers_stop(self, handler_uuid):
        r = self.stop_browser(handler_uuid)
        return r

    """ Connectors to browser API """

    browserEndpoint = "http://distinct-browser"

    def get_browsers(self):
        r = requests.get(f"{self.browserEndpoint}/api/browsers")
        return r.json()

    def get_browsers_by_handler(self, handler_uuid):
        r = requests.get(f"{self.browserEndpoint}/api/browsers/{handler_uuid}")
        return r.json()

    def start_browser(self, handler_uuid):
        r = requests.post(f"{self.browserEndpoint}/api/browsers/{handler_uuid}/start")
        return r.json()

    def stop_browser(self, handler_uuid):
        r = requests.post(f"{self.browserEndpoint}/api/browsers/{handler_uuid}/stop")
        return r.json()
