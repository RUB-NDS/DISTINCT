import json

from model.EventProcessor import EventProcessor

class WindowPropChangedProcessor(EventProcessor):
    """ WINDOW PROP CHANGED
        -> hierarchy, href, hrefparts, key, val, valtype
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Window Property Changed",
            {
                "Key": self.val["key"],
                "Value Type": self.val["valtype"],
                "Value": json.dumps(self.val["val"])
            },
            linebreaks=300
        )
