from model.EventProcessor import EventProcessor

class BroadcastChannelNewProcessor(EventProcessor):
    """ BROADCAST CHANNEL NEW
        -> hierarchy, href, hrefparts, channel_name
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Broadcast Channel New",
            {
                "Channel Name": self.val["channel_name"]
            }
        )
