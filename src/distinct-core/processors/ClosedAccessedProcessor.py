from model.ReportProcessor import ReportProcessor

class ClosedAccessedProcessor(ReportProcessor):
    """ CLOSED ACCESSED
        -> hierarchy, href, hrefparts, closed
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Closed Accessed",
            {
                "Closed": "True" if self.val["closed"] else "False"
            }
        )
