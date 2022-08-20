from model.ReportProcessor import ReportProcessor

class RefreshRedirectProcessor(ReportProcessor):
    """ REFRESH REDIRECT
        -> hierarchy, href, hrefparts, wait_seconds, location, status_code
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Refresh Redirect",
            {
                "Status Code": self.val["status_code"],
                "Wait Seconds": self.val["wait_seconds"],
                "Location": self.val["location"]
            }
        )
