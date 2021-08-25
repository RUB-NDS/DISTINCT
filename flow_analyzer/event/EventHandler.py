import logging

from threading import Thread
from queue import Queue
from model.ExecutionContext import ExecutionContext

logger = logging.getLogger(__name__)

class EventHandler(Thread):

    def __init__(self, event_dispatcher):
        logger.info("Initializing new event handler thread")
        super(EventHandler, self).__init__()
        self.daemon = True
        
        self.queue = Queue()
        event_dispatcher.register_handler(self)

    def run(self):
        logger.info("Started event handler thread")

        execution_context = ExecutionContext()
        logger.info("Created new execution context")

        while True:
            # Two types of messages can be added to the queue
            # {"report": {...}} -> from chrome extension
            # {"cmd": {...}} -> from cli tool
            message = self.queue.get()
            logger.debug("Dispatched message: {}".format(message))

            # Process message ...
            execution_context.process_report(message)

    def queue_message(self, message):
        self.queue.put(message)
