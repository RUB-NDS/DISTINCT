from model.ReportProcessor import ReportProcessor

class MetaReloadProcessor(ReportProcessor):
    """ META RELOAD
        -> hierarchy, href, hrefparts, wait_seconds
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Meta Reload",
            {
                "Wait Seconds": self.val["wait_seconds"]
            }
        )
