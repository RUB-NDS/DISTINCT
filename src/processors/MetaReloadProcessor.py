from model.EventProcessor import EventProcessor

class MetaReloadProcessor(EventProcessor):
    """ META RELOAD
        -> hierarchy, href, hrefparts, wait_seconds
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Meta Reload",
            {
                "Wait Seconds": self.val["wait_seconds"],
                "Source": self.val["href"]
            }
        )
