import json

from model.EventProcessor import EventProcessor

class AddEventListenerProcessor(EventProcessor):
    """ ADD EVENT LISTENER
        -> hierarchy, href, hrefparts, type, method, callback
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Add Event Listener",
            {
                "Type": self.val["type"],
                "Method": self.val["method"],
                "Callback": json.dumps(self.val["callback"])
            }
        )
