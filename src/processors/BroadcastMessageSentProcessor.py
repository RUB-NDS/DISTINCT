import json

from model.EventProcessor import EventProcessor

class BroadcastMessageSentProcessor(EventProcessor):
    """ BROADCAST MESSAGE SENT
        -> hierarchy, href, hrefparts, channel_name, source_frame, data, data_type
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

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
