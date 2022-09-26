import logging
import sys
import os
from model.ReportDispatcher import ReportDispatcher

logger = logging.getLogger(__name__)

def main():
    verbosity = os.environ["VERBOSITY"]
    level = logging.getLevelName(verbosity) if verbosity else logging.DEBUG
    logging.basicConfig(stream=sys.stdout, level=level)
    logging.getLogger(__name__).setLevel(level)
    logging.getLogger('werkzeug').setLevel(level)
    logger.info(f"Log level: {level}")

    report_dispatcher = ReportDispatcher()
    report_dispatcher.start()
    report_dispatcher.join()

if __name__ == "__main__":
    main()
