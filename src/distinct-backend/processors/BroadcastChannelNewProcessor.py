from model.ReportProcessor import ReportProcessor

class BroadcastChannelNewProcessor(ReportProcessor):
    """ BROADCAST CHANNEL NEW
        -> hierarchy, href, hrefparts, channel_name
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Broadcast Channel New",
            {
                "Channel Name": self.val["channel_name"]
            }
        )
