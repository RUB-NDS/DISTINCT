from model.ReportProcessor import ReportProcessor

class RefreshReloadProcessor(ReportProcessor):
    """ REFRESH RELOAD
        -> hierarchy, href, hrefparts, wait_seconds, status_code
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Refresh Reload",
            {
                "Status Code": self.val["status_code"],
                "Wait Seconds": self.val["wait_seconds"]
            }
        )
