from urllib import parse
from urllib.parse import urlparse
from model.ReportProcessor import ReportProcessor
from processors.PostMessageReceivedProcessor import PostMessageReceivedProcessor

class LocationSetProcessor(ReportProcessor):
    """ LOCATION SET
        -> hierarchy, href, hrefparts, prop, target
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        keyval = {
            "Property": self.val["prop"],
            "Target": self.val["target"]
        }
        color = None

        # Check for relative redirects
        if self.relative_redirect(self.val["prop"], self.val["target"]):
            keyval["Info"] = (
                "Detected potential relative redirect. Check if this redirect contains "
                "confidential data and is performed across windows."
            )
            color="orange"

        else:

            # Check if redirect target comes from user input
            related_events = self.search_userinput(ctx, self.val["prop"], self.val["target"])

            if related_events:
                keyval["Info"] = (
                    "Detected that the redirect target potentially depends on "
                    "user input. Check if the user input in the related events influences the "
                    "redirect target by actively modifying it."
                )
                keyval["Related Events"] = ", ".join(str(processor.id) for processor in related_events)
                color = "orange"

            else:
                color = "green"

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Location Set",
            keyval,
            color = color
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

    @staticmethod
    def search_userinput(ctx, property, target):
        """ Search all events in reverse order that can contain user input for the url.
            Example: If "https://example.com" is used in postMessage or location set,
            then search all previous events that can contain user input as GET / POST
            parameters for this url. If some event like "Document Init" contains this url
            as GET parameter, we want to include this event as a related event to this event.

            Returns a list of related events (event processors).
        """

        # If the location is set with a method that can
        # 1) change its origin and
        # 2) include confidential data in params like query or fragment
        if (
            property == "href"
            or property == "assign"
            or property == "replace"
        ):
            parsed = urlparse(target)
            search_url = ""

            if parsed.scheme: search_url += f"{parsed.scheme}://"
            if parsed.netloc: search_url += parsed.netloc
            if parsed.path: search_url += parsed.path
            # We do not want to search for the query or fragment, as these probably do not come
            # from the user input (i.e., the query might contain a token)

            if search_url:
                return PostMessageReceivedProcessor.search_userinput(ctx.processors, search_url)
            else:
                return []
