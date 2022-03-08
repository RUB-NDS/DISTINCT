from model.ReportProcessor import ReportProcessor

class MetaRedirectProcessor(ReportProcessor):
    """ META REDIRECT
        -> hierarchy, href, hrefparts, wait_seconds, location
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Meta Redirect",
            {
                "Wait Seconds": self.val["wait_seconds"],
                "Location": self.val["location"]
            }
        )
