import json

from model.EventProcessor import EventProcessor

class SessionStorageSetProcessor(EventProcessor):
    """ SESSIONSTORAGE SET
        -> hierarchy, href, hrefparts, key, val
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "SessionStorage Set",
            {
                "Key": self.val["key"],
                "Value": json.dumps(self.val["val"])
            }
        )
