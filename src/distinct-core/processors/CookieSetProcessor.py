import json
from model.ReportProcessor import ReportProcessor

class CookieSetProcessor(ReportProcessor):
    """ COOKIE SET
        -> hierarchy, href, hrefparts, val
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Cookie Set",
            {
                "Value": json.dumps(self.val["val"])
            }
        )
