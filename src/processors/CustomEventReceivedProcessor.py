import json

from model.EventProcessor import EventProcessor

class CustomEventReceivedProcessor(EventProcessor):
    """ CUSTOM EVENT RECEIVED
        -> hierarchy, href, hrefparts, type, data, data_type
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Custom Event Received",
            {
                "Type": self.val["type"],
                "Data Type": self.val["data_type"],
                "Data": json.dumps(self.val["data"])
            }
        )
