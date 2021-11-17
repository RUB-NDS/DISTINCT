from model.EventProcessor import EventProcessor

class DocumentLoadingProcessor(EventProcessor):
    """ DOCUMENT LOADING
        The document is still loading.
        -> hierarchy, href, hrefparts
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)
