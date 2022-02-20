class ReportProcessor:
    """ Base class for all report processors.
        A report processor receives a report as input, processes it, and creates some output.
        The report processing part is optional and may only be implemented for some reports.
        The output can range from log files to entries in a sequence diagram.
    """

    def __init__(self, ctx, report):

        # Store reference to execution context in which this report was received
        self.ctx = ctx

        # Extract the main parts of the report
        # report = {"id": int, "timestamp": str, "key": str, "val": any}
        self.id = report["id"]
        self.timestamp = report["timestamp"]
        self.key = report["key"]
        self.val = report["val"]
