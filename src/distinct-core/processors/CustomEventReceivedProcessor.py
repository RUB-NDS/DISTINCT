import json
from model.ReportProcessor import ReportProcessor

class CustomEventReceivedProcessor(ReportProcessor):
    """ CUSTOM EVENT RECEIVED
        -> hierarchy, href, hrefparts, type, data, data_type, source_frame, target_frame
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.arrow(
            self.val["source_frame"],
            self.val["target_frame"],
            "Custom Event Received"
        )

        ctx.sequencediagram.note(
            self.val["target_frame"],
            self.id,
            self.timestamp,
            "Custom Event Received",
            {
                "Type": self.val["type"],
                "Data Type": self.val["data_type"],
                "Data": json.dumps(self.val["data"])
            }
        )
