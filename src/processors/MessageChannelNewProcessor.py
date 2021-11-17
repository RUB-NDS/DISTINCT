from model.EventProcessor import EventProcessor

class MessageChannelNewProcessor(EventProcessor):
    """ MESSAGE CHANNEL NEW
        -> hierarchy, href, hrefparts, channel_id
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Message Channel New",
            {
                "Channel ID": f"#{self.val['channel_id']}"
            }
        )
