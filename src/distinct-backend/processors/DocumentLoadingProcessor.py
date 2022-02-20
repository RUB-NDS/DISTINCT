from model.ReportProcessor import ReportProcessor

class DocumentLoadingProcessor(ReportProcessor):
    """ DOCUMENT LOADING
        The document is still loading.
        -> hierarchy, href, hrefparts
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)
