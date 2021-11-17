from model.EventProcessor import EventProcessor

class HTTPRedirectProcessor(EventProcessor):
    """ HTTP REDIRECT
        -> hierarchy, href, hrefparts, status_code, location
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

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
