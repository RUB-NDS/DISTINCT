from model.EventProcessor import EventProcessor

class MetaRedirectProcessor(EventProcessor):
    """ META REDIRECT
        -> hierarchy, href, hrefparts, wait_seconds, location
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

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
