import json

from model.EventProcessor import EventProcessor

class PostMessageReceivedProcessor(EventProcessor):
    """ POSTMESSAGE RECEIVED
        -> hierarchy, href, hrefparts, receiver, sender, data, datatype,
        ports = [{channel_id, port_id}], targetorigincheck, sourceoriginaccessed = "yes"/"no"
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.arrow(
            self.val["sender"],
            self.val["receiver"],
            "PostMessage Received"
        )

        ctx.sequencediagram.note(
            self.val["receiver"],
            self.id,
            self.timestamp,
            "PostMessage Received",
            {
                "Target Origin Check": self.val["targetorigincheck"],
                "Data Type": self.val["datatype"],
                "Data": json.dumps(self.val["data"]),
                "Ports": json.dumps(self.val["ports"])
            },
            color = ("red" if self.val["targetorigincheck"] == "*" else "green")
        )
