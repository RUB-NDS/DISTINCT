import logging
from model.ReportDispatcher import ReportDispatcher

logger = logging.getLogger(__name__)

def main():
    report_dispatcher = ReportDispatcher()
    report_dispatcher.start()
    report_dispatcher.join()

if __name__ == "__main__":
    main()
