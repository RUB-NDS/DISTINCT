import json
from model.ReportProcessor import ReportProcessor

class IndexedDBSetProcessor(ReportProcessor):
    """ INDEXEDDB ADD/PUT
        -> hierarchy, href, hrefparts, db, objectstore, keypath, key, val
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "IndexedDB Set",
            {
                "Database": self.val["db"],
                "Object Store": self.val["objectstore"],
                "Key Path": self.val["keypath"],
                "Key": self.val["key"],
                "Value": json.dumps(self.val["val"])
            }
        )
