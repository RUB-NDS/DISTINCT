import json

from model.EventProcessor import EventProcessor

class BroadcastMessageReceivedProcessor(EventProcessor):
    """ BROADCAST MESSAGE RECEIVED
        -> hierarchy, href, hrefparts, channel_name, target_frame, data, data_type
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

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
