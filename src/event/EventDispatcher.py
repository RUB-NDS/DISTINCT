import logging

from threading import Thread
from http.server import HTTPServer

from event.EventServerHandler import EventServerHandler

logger = logging.getLogger(__name__)

class EventDispatcher(Thread):

    def __init__(self):
        logger.info("Initializing event dispatcher thread")
        super(EventDispatcher, self).__init__()
        self.daemon = True

        self.registered_handlers = []
    
    def run(self):
        logger.info("Started event dispatcher thread")

        listen_port = 20200
        logger.info(f"Starting event server on port {listen_port}")
        
        event_server_handler = EventServerHandler(self)
        self.httpd = HTTPServer(("127.0.0.1", listen_port), event_server_handler)
        self.httpd.serve_forever()

    def register_handler(self, thread):
        self.registered_handlers.append(thread)
    
    def dispatch_message(self, message):
        for thread in self.registered_handlers:
            thread.queue_message(message)
