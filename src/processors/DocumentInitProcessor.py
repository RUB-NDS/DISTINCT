from model.Frame import Frame
from model.EventProcessor import EventProcessor

class DocumentInitProcessor(EventProcessor):
    """ DOCUMENT INIT
        The document is initiated. Since the extension is executed before any other scripts on the
        page, this state catches the page before any other JS redirects or similar are executed.
        -> hierarchy, href, hrefparts
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        frame = Frame(href=self.val["href"])
        ctx.insert_frame(self.val["hierarchy"], frame)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Document Init",
            {
                "URL": self.val["href"]
            },
            color="orange"
        )
