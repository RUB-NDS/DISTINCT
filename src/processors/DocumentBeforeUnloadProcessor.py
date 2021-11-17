from model.EventProcessor import EventProcessor

class DocumentBeforeUnloadProcessor(EventProcessor):
    """ DOCUMENT BEFOREUNLOAD
        The document and its resources are about to be unloaded.
        -> hierarchy, href, hrefparts
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        frame = ctx.get_frame(self.val["hierarchy"])
        if frame:
            ctx.sequencediagram.note(
                self.val["hierarchy"],
                self.id,
                self.timestamp,
                "Document Before Unload",
                {}
            )
            ctx.remove_frame(self.val["hierarchy"])
