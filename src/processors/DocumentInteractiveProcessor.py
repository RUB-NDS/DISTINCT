from model.Frame import Frame
from model.EventProcessor import EventProcessor

class DocumentInteractiveProcessor(EventProcessor):
    """ DOCUMENT INTERACTIVE
        The document has finished loading. We can now access the DOM elements.
        But sub-resources such as scripts and frames are still loading.
        -> hierarchy, href, hrefparts, html
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        frame = Frame(href=self.val["href"], html=self.val["html"])
        ctx.insert_frame(self.val["hierarchy"], frame)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Document Interactive",
            {
                "URL": self.val["href"],
                "HTML": self.val["html"]
            },
            linebreaks=300
        )
