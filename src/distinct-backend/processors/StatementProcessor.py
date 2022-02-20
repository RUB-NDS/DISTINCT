from model.ReportProcessor import ReportProcessor

class StatementProcessor(ReportProcessor):
    """ STATEMENT
        -> hierarchy, href, hrefparts, key, val
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        if self.val["key"] not in ctx.statements:
            ctx.statements[self.val["key"]] = [self.val["val"]]
        else:
            ctx.statements[self.val["key"]].append(self.val["val"])
