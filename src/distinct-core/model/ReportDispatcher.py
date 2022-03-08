import logging
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

        self.report_handlers = {}
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
        self.app.add_url_rule("/api/handlers", view_func=self.handlers, methods=["GET", "POST"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/stop", view_func=self.stop_handler, methods=["POST"])

        # Reports
        self.app.add_url_rule("/api/handlers/<handler_uuid>/dispatch", view_func=self.dispatch_on_handler, methods=["POST"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/reports", view_func=self.reports_on_handler, methods=["GET"])
        self.app.add_url_rule("/api/handlers/<handler_uuid>/svg", view_func=self.svg_on_handler, methods=["GET"])

    """ Report Handler Routines """

    def new_report_handler(self):
        report_handler = ReportHandler(self)
        report_handler.start()
        self.report_handlers[report_handler.uuid] = report_handler
        return report_handler

    def stop_report_handler(self, handler_uuid):
        if self.report_handlers[handler_uuid].is_alive():
            self.report_handlers[handler_uuid].stop()

    def pass_report_to_handler(self, report, handler_uuid):
        # report = {"report": {"key": str, "val": any}}
        if handler_uuid in self.report_handlers:
            self.report_handlers[handler_uuid].queue_report(report)
            return True
        else:
            logger.error(f"Failed to dispatch report to report handler with uuid"
            f" {handler_uuid} because the report handler does not exist")
            return False

    """ Webserver Decorators """

    def check_handler_existence(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            dispatcher = args[0]
            handler_uuid = kwargs["handler_uuid"]
            if handler_uuid in dispatcher.report_handlers:
                return func(*args, **kwargs)
            else:
                logger.error(f"Report handler with uuid {handler_uuid} does not exist")
                body = {"success": False, "error": "Report handler does not exist", "data": None}
                return body
        return wrapper

    """ Webserver Frontend Routes """

    # GET /
    def index(self):
        return redirect("/app", 302)

    # GET /app
    # GET /app/<path:path>
    def frontend(self, path):
        return self.app.send_static_file("index.html")

    """ Webserver API Routes """

    # GET|POST /handlers
    def handlers(self):
        if request.method == "GET":
            body = {"success":True, "error": None, "data": []}
            for uuid, handler in self.report_handlers.items():
                body["data"].append({
                    "uuid": uuid,
                    "running": handler.is_alive(),
                    "starttime": handler.starttime,
                    "reportsCount": handler.counter,
                    "queueSize": handler.queue.qsize()
                })
            return body
        elif request.method == "POST":
            report_handler = self.new_report_handler()
            body = {
                "success":True,
                "error": None,
                "data": {
                    "uuid": report_handler.uuid,
                    "running": report_handler.is_alive(),
                    "starttime": report_handler.starttime,
                    "reportsCount": report_handler.counter,
                    "queueSize": report_handler.queue.qsize()
                }
            }
            return body

    # POST /handlers/<handler_uuid>/stop
    @check_handler_existence
    def stop_handler(self, handler_uuid):
        self.stop_report_handler(handler_uuid)
        body = {"success": True, "error": None, "data": None}
        return body

    # POST /handlers/<handler_uuid>/dispatch
    @check_handler_existence
    def dispatch_on_handler(self, handler_uuid):
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

    # GET /handlers/<handler_uuid>/reports
    @check_handler_existence
    def reports_on_handler(self, handler_uuid):
        body = {
            "success":True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "reports": self.report_handlers[handler_uuid].ctx.reports
            }
        }
        return body

    # GET /handlers/<handler_uuid>/svg
    @check_handler_existence
    def svg_on_handler(self, handler_uuid):
        body = {
            "success":True,
            "error": None,
            "data": {
                "uuid": handler_uuid,
                "svg": self.report_handlers[handler_uuid].ctx.sequencediagram.svg()
            }
        }
        return body
