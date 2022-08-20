import logging
import time
from uuid import uuid4
from threading import Thread
from queue import Empty, Queue
from model.ExecutionContext import ExecutionContext
from model.ReportHandlerStatus import ReportHandlerStatus

logger = logging.getLogger(__name__)

class ReportHandler(Thread):

    def __init__(self, report_dispatcher, uuid=None, config={}):
        logger.info("Initializing report handler thread")
        super(ReportHandler, self).__init__()

        self.report_dispatcher = report_dispatcher
        self.db = self.report_dispatcher.db
        self.queue = Queue()
        self.should_stop = False

        # Check if handler exists in database
        if (
            uuid is not None
            and self.db["distinct"]["handlers"].find_one({"handler_uuid": uuid})
            is not None
        ):
            # Handler already exists -> use existing handler
            self.uuid = uuid
            self.counter = self.db["distinct"]["handlers"].find_one(
                {"handler_uuid": uuid}
            )["handler"]["counter"]
        else:
            # Handler does not exist -> create new handler
            self.uuid = uuid or str(uuid4())
            self.counter = 0
            self.db["distinct"]["handlers"].insert_one({
                "handler_uuid": self.uuid,
                "handler": {
                    "uuid": self.uuid,
                    "starttime": str(int(time.time())),
                    "config": config,
                    "status": ReportHandlerStatus.INIT.value,
                    "counter": self.counter
                }
            })

        # Initialize execution environment
        self.ctx = ExecutionContext(self)

    @property
    def starttime(self):
        d = self.db["distinct"]["handlers"].find_one({"handler_uuid": self.uuid})
        return d["handler"]["starttime"]

    @property
    def config(self):
        d = self.db["distinct"]["handlers"].find_one({"handler_uuid": self.uuid})
        return d["handler"]["config"]

    @property
    def status(self):
        d = self.db["distinct"]["handlers"].find_one({"handler_uuid": self.uuid})
        return ReportHandlerStatus(d["handler"]["status"])

    def run(self):
        logger.info("Starting report handler thread")
        self.db["distinct"]["handlers"].update_one(
            {"handler_uuid": self.uuid},
            {"$set": {"handler.status": ReportHandlerStatus.RUNNING.value}}
        )

        while True and not self.should_stop:
            # {"id": int, "timestamp": str, "key": str, "val": any}
            try:
                report = self.queue.get(timeout=1)

                # Process report
                logger.debug(f"Report handler {self.uuid} processes report: {report}")
                self.ctx.process_report(report)
            except Empty:
                continue
            except Exception as e:
                logger.exception(f"Uncaught exception in report handler {self.uuid}: {e}")
                continue

        logger.info("Stopping report handler thread")
        self.db["distinct"]["handlers"].update_one(
            {"handler_uuid": self.uuid},
            {"$set": {"handler.status": ReportHandlerStatus.STOPPED.value}}
        )

    def stop(self):
        logger.info("Received signal to stop report handler thread")
        self.should_stop = True

    def queue_report(self, report):
        report_copy = report["report"].copy()
        report_copy["id"] = self.counter
        report_copy["timestamp"] = str(time.time())

        self.queue.put(report_copy)
        self.counter += 1
        self.db["distinct"]["handlers"].update_one(
            {"handler_uuid": self.uuid},
            {"$inc": {"handler.counter": 1}}
        )
