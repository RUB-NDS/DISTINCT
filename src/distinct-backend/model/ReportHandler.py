import logging
import time
from uuid import uuid4
from threading import Thread
from queue import Queue
from model.ExecutionContext import ExecutionContext

logger = logging.getLogger(__name__)

class ReportHandler(Thread):

    def __init__(self, report_dispatcher):
        logger.info("Initializing report handler thread")
        super(ReportHandler, self).__init__()
        self.daemon = True

        self.report_dispatcher = report_dispatcher

        self.uuid = str(uuid4())
        self.starttime = str(time.time())

        self.queue = Queue()
        self.counter = 0

        self.ctx = ExecutionContext(self)

    def run(self):
        logger.info("Starting report handler thread")
        while True:
            # {"id": int, "timestamp": str, "key": str, "val": any}
            report = self.queue.get()
            logger.debug(f"Report handler {self.uuid} processes report: {report}")

            # Process report
            self.ctx.process_report(report)

    def queue_report(self, report):
        report_copy = report["report"].copy()
        report_copy["id"] = self.counter
        report_copy["timestamp"] = str(time.time())

        self.queue.put(report_copy)
        self.counter += 1
