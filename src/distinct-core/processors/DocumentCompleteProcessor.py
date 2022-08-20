from model.ReportProcessor import ReportProcessor

class DocumentCompleteProcessor(ReportProcessor):
    """ DOCUMENT COMPLETED
        The page is fully loaded.
        -> hierarchy, href, hrefparts, html
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)
