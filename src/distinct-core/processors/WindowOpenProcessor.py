from model.Frame import Frame
from model.ReportProcessor import ReportProcessor

class WindowOpenProcessor(ReportProcessor):
    """ WINDOW OPEN
        -> hierarchy, href, hrefparts, url, popup_hierarchy
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        frame = Frame(href=self.val["url"])
        ctx.insert_frame(self.val["popup_hierarchy"], frame)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Window Open",
            {
                "URL": self.val["url"]
            }
        )

        ctx.sequencediagram.arrow(
            self.val["hierarchy"],
            self.val["popup_hierarchy"],
            "Window Open"
        )
