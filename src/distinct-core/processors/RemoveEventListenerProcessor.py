from model.ReportProcessor import ReportProcessor

class RemoveEventListenerProcessor(ReportProcessor):
    """ REMOVE EVENT LISTENER
        -> hierarchy, href, hrefparts, type, method, callback
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Remove Event Listener",
            {
                "Type": self.val["type"],
                "Method": self.val["method"],
                "Callback": self.val["callback"]
            }
        )
