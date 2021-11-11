import logging

from threading import Thread
from queue import Queue

from model.ExecutionContext import ExecutionContext

logger = logging.getLogger(__name__)

class EventHandler(Thread):

    def __init__(self, event_dispatcher, config = {}):
        logger.info("Initializing event handler thread")
        super(EventHandler, self).__init__()
        
        self.daemon = True
        self.queue = Queue()
        self.execution_context = ExecutionContext(config)

        event_dispatcher.register_handler(self)

    def run(self):
        logger.info("Started event handler thread")

        while True:
            # Events from chrome extension:
            # {"event": {"key": "...", "val": {...}}}
            event = self.queue.get()
            logger.debug(f"Dispatch event: {event}")

            # Process event
            self.execution_context.process_event(event["event"])

    def queue_event(self, event):
        self.queue.put(event)
