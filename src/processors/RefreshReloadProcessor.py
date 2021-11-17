from model.EventProcessor import EventProcessor

class RefreshReloadProcessor(EventProcessor):
    """ REFRESH RELOAD
        -> hierarchy, href, hrefparts, wait_seconds, status_code
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Refresh Reload",
            {
                "Status Code": self.val["status_code"],
                "Wait Seconds": self.val["wait_seconds"]
            }
        )
