from model.Frame import Frame
from model.ReportProcessor import ReportProcessor

class WindowCloseProcessor(ReportProcessor):
    """ WINDOW CLOSE
        -> hierarchy, href, hrefparts, opener_hierarchy
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        old_frame = ctx.get_frame(self.val["hierarchy"])

        if old_frame:
            ctx.sequencediagram.note(
                self.val["hierarchy"],
                self.id,
                self.timestamp,
                "Window Close",
                {}
            )

            ctx.sequencediagram.arrow(
                self.val["hierarchy"],
                self.val["opener_hierarchy"],
                "Window Close"
            )

            ctx.remove_frame(self.val["hierarchy"])
