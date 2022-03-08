from model.ReportProcessor import ReportProcessor

class MessageChannelNewProcessor(ReportProcessor):
    """ MESSAGE CHANNEL NEW
        -> hierarchy, href, hrefparts, channel_id
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Message Channel New",
            {
                "Channel ID": f"#{self.val['channel_id']}"
            }
        )
