import json
from model.ReportProcessor import ReportProcessor

class BroadcastMessageSentProcessor(ReportProcessor):
    """ BROADCAST MESSAGE SENT
        -> hierarchy, href, hrefparts, channel_name, source_frame, data, data_type
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["source_frame"],
            self.id,
            self.timestamp,
            "Broadcast Message Sent",
            {
                "Channel Name": self.val["channel_name"],
                "Data Type": self.val["data_type"],
                "Data": json.dumps(self.val["data"])
            }
        )
