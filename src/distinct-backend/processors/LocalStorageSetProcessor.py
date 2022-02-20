import json
from model.ReportProcessor import ReportProcessor

class LocalStorageSetProcessor(ReportProcessor):
    """ LOCALSTORAGE SET
        -> hierarchy, href, hrefparts, key, val
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "LocalStorage Set",
            {
                "Key": self.val["key"],
                "Value": json.dumps(self.val["val"])
            }
        )
