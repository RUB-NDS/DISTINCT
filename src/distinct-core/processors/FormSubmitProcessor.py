import json

from model.Frame import Frame
from model.ReportProcessor import ReportProcessor

class FormSubmitProcessor(ReportProcessor):
    """ FORM SUBMITTED
        -> hierarchy, href, hrefparts, action, form
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        frame = Frame(href=self.val["action"])
        ctx.insert_frame(self.val["hierarchy"], frame)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Form Submit",
            {
                "URL": self.val["action"],
                "Body": json.dumps(self.val["form"])
            }
        )
