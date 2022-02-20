import json
from model.ReportProcessor import ReportProcessor

class WindowPropChangedProcessor(ReportProcessor):
    """ WINDOW PROP CHANGED
        -> hierarchy, href, hrefparts, key, val, valtype
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Window Property Changed",
            {
                "Key": self.val["key"],
                "Value Type": self.val["valtype"],
                "Value": json.dumps(self.val["val"]) if "val" in self.val else ""
            },
            linebreaks=300
        )
