from model.EventProcessor import EventProcessor

class ClosedAccessedProcessor(EventProcessor):
    """ CLOSED ACCESSED
        -> hierarchy, href, hrefparts, closed
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Closed Accessed",
            {
                "Closed": "True" if self.val["closed"] else "False"
            }
        )
