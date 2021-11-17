from model.EventProcessor import EventProcessor

class LocationSetProcessor(EventProcessor):
    """ LOCATION SET
        -> hierarchy, href, hrefparts, prop, target
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        if self.relative_redirect(self.val["prop"], self.val["target"]):
            # Relative Redirect
            ctx.sequencediagram.note(
                self.val["hierarchy"],
                self.id,
                self.timestamp,
                "Location Set",
                {
                    "Property": self.val["prop"],
                    "Target": self.val["target"],
                    "Info": "Detected potential relative redirect. Check if this redirect contains "
                            "confidential data and is performed across windows."
                },
                color="orange"
            )
        else:
            # Normal Redirect
            ctx.sequencediagram.note(
                self.val["hierarchy"],
                self.id,
                self.timestamp,
                "Location Set",
                {
                    "Property": self.val["prop"],
                    "Target": self.val["target"]
                }
            )

    @staticmethod
    def relative_redirect(property, target):
        """ Check if the target of the location set event is a relative redirect
            Returns True, if target is a relative redirect.
            Returns False, if target is not a relative redirect.
        """
        
        # If location is set via href, assign, or replace, and starts with "/", it is relative
        if (
            (
                property == "href"
                or property == "assign"
                or property == "replace"
            )
            and
            (
                target.startswith("/")
                and not target.startswith("//") # ignore "//example.com" -> "https://example.com"
            )
        ):
            return True
        
        # If location is set via pathname, it is always a relative redirect
        elif (property == "pathname"):
            return True
        
        else:
            return False
