from model.EventProcessor import EventProcessor

class LocationSetProcessor(EventProcessor):
    """ LOCATION SET
        -> hierarchy, href, hrefparts, prop, target
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Location Set",
            {
                "Property": self.val["prop"],
                "Source": self.val["href"],
                "Target": self.val["target"]
            }
        )
