from model.ReportProcessor import ReportProcessor

class HTTPRedirectProcessor(ReportProcessor):
    """ HTTP REDIRECT
        -> hierarchy, href, hrefparts, status_code, location
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "HTTP Redirect",
            {
                "Status Code": self.val["status_code"],
                "Location": self.val["location"]
            }
        )
