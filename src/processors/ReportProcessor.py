from model.EventProcessor import EventProcessor

class ReportProcessor(EventProcessor):
    """ REPORT
        -> hierarchy, href, hrefparts, key, val
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.process_report(self.val["key"], self.val["val"])
