import json
from model.ReportProcessor import ReportProcessor

class CustomEventNewProcessor(ReportProcessor):
    """ CUSTOM EVENT NEW
        -> hierarchy, href, hrefparts, type, data, data_type
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Custom Event New",
            {
                "Type": self.val["type"],
                "Data Type": self.val["data_type"],
                "Data": json.dumps(self.val["data"])
            }
        )
