import logging
import time
from uuid import uuid4
from threading import Thread
from queue import Empty, Queue
from model.ExecutionContext import ExecutionContext

logger = logging.getLogger(__name__)

class ReportHandler(Thread):

    def __init__(self, report_dispatcher, config):
        logger.info("Initializing report handler thread")
        super(ReportHandler, self).__init__()
        self.should_stop = False

        self.report_dispatcher = report_dispatcher
        self.config = config

        self.uuid = str(uuid4())
        self.starttime = str(int(time.time()))

        self.queue = Queue()
        self.counter = 0

        self.ctx = ExecutionContext(self)

    def run(self):
        logger.info("Starting report handler thread")
        while True and not self.should_stop:
            # {"id": int, "timestamp": str, "key": str, "val": any}
            try:
                report = self.queue.get(timeout=10)

                # Process report
                logger.debug(f"Report handler {self.uuid} processes report: {report}")
                self.ctx.process_report(report)
            except Empty:
                continue
            except Exception as e:
                logger.exception(f"Uncaught exception in report handler {self.uuid}: {e}")
                continue
        logger.info("Stopping report handler thread")

    def stop(self):
        logger.info("Received signal to stop report handler thread")
        self.should_stop = True

    def queue_report(self, report):
        report_copy = report["report"].copy()
        report_copy["id"] = self.counter
        report_copy["timestamp"] = str(time.time())

        self.queue.put(report_copy)
        self.counter += 1
