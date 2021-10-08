import json
import logging

from http.server import SimpleHTTPRequestHandler

logger = logging.getLogger(__name__)

class EventServerHandler(SimpleHTTPRequestHandler):
    """ HTTP server receiving events from the chrome extension """

    def __init__(self, event_dispatcher):
        self.event_dispatcher = event_dispatcher
    
    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        """ Receive events as POST requests from the chrome extension

            In chrome extension: _event("foo", {"bar": "baz"})
            POST request body: {"event": {"key": "foo", "val": {"bar": "baz"}}}
        """
        
        contentlength = int(self.headers['Content-Length'])
        postdata = self.rfile.read(contentlength)

        try:
            postdatajson = json.loads(postdata)
            if "event" not in postdatajson:
                raise Exception("Validation of received event failed")
            if ("key" not in postdatajson["event"]) or ("val" not in postdatajson["event"]):
                raise Exception("Validation of received event failed")
        except Exception as e:
            logger.exception(e)
            self.respond(False)
            return

        self.event_dispatcher.dispatch_event(postdatajson)
        self.respond(True)

    def respond(self, success):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if success:
            self.wfile.write(json.dumps({"success": True}).encode("utf8"))
        else:
            self.wfile.write(json.dumps({"success": False}).encode("utf8"))

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        return super(EventServerHandler, self).end_headers()

    def log_message(self, format, *args):
        # We already log the event; thus we skip it here ...
        return
