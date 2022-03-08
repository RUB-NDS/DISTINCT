import json
from model.ReportProcessor import ReportProcessor

class BroadcastMessageReceivedProcessor(ReportProcessor):
    """ BROADCAST MESSAGE RECEIVED
        -> hierarchy, href, hrefparts, channel_name, target_frame, data, data_type
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["target_frame"],
            self.id,
            self.timestamp,
            "Broadcast Message Received",
            {
                "Channel Name": self.val["channel_name"],
                "Data Type": self.val["data_type"],
                "Data": json.dumps(self.val["data"])
            }
        )
