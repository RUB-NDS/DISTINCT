from model.EventProcessor import EventProcessor

class RemoveEventListenerProcessor(EventProcessor):
    """ REMOVE EVENT LISTENER
        -> hierarchy, href, hrefparts, type, method, callback
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Remove Event Listener",
            {
                "Type": self.val["type"],
                "Method": self.val["method"],
                "Callback": self.val["callback"]
            }
        )
