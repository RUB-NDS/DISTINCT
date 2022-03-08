import logging
import sys
from model.ReportDispatcher import ReportDispatcher

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    report_dispatcher = ReportDispatcher()
    report_dispatcher.start()
    report_dispatcher.join()

if __name__ == "__main__":
    main()
