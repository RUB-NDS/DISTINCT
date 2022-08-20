import json
from model.ReportProcessor import ReportProcessor

class WindowPropNewProcessor(ReportProcessor):
    """ WINDOW PROP NEW
        -> hierarchy, href, hrefparts, key, val, valtype
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Window Property New",
            {
                "Key": self.val["key"],
                "Value Type": self.val["valtype"],
                "Value": json.dumps(self.val["val"]) if "val" in self.val else ""
            },
            linebreaks=300
        )
