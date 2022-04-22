from model.ReportProcessor import ReportProcessor

class StatementProcessor(ReportProcessor):
    """ STATEMENT
        -> hierarchy, href, hrefparts, key, val
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        stm_key = self.val["key"]
        stm_val = self.val["val"]

        if stm_key not in ctx.statements:
            ctx.statements[stm_key] = stm_val
        elif type(ctx.statements[stm_key]) is list and stm_val not in ctx.statements[stm_key]:
            ctx.statements[stm_key].append(stm_val)
        elif type(ctx.statements[stm_key]) is not list and stm_val != ctx.statements[stm_key]:
            ctx.statements[stm_key] = [ctx.statements[stm_key]] + [stm_val]
