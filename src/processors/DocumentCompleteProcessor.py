from model.EventProcessor import EventProcessor

class DocumentCompleteProcessor(EventProcessor):
    """ DOCUMENT COMPLETED
        The page is fully loaded.
        -> hierarchy, href, hrefparts, html
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)
