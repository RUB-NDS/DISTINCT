from model.EventProcessor import EventProcessor

class RefreshRedirectProcessor(EventProcessor):
    """ REFRESH REDIRECT
        -> hierarchy, href, hrefparts, wait_seconds, location, status_code
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Refresh Redirect",
            {
                "Status Code": self.val["status_code"],
                "Wait Seconds": self.val["wait_seconds"],
                "Source": self.val["href"],
                "Location": self.val["location"]
            }
        )
