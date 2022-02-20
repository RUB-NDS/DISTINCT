import json
from model.ReportProcessor import ReportProcessor

class MessageChannelReceivedProcessor(ReportProcessor):
    """ CHANNEL MESSAGE RECEIVED
        -> hierarchy, href, hrefparts, channel_id, port_id, source_frame, target_frame, data, data_type
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.arrow(
            self.val["source_frame"],
            self.val["target_frame"],
            f"&#35;{self.val['channel_id']}.{self.val['port_id']}.postMessage()"
        )

        ctx.sequencediagram.note(
            self.val["target_frame"],
            self.id,
            self.timestamp,
            "Channel Message Received",
            {
                "Channel ID": f'#{self.val["channel_id"]}',
                "Port ID": self.val["port_id"],
                "Data Type": self.val["data_type"],
                "Data": json.dumps(self.val["data"])
            }
        )
