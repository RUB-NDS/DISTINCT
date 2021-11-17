import json

from model.EventProcessor import EventProcessor

class CookieSetProcessor(EventProcessor):
    """ COOKIE SET
        -> hierarchy, href, hrefparts, val
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Cookie Set",
            {
                "Value": json.dumps(self.val["val"])
            }
        )
