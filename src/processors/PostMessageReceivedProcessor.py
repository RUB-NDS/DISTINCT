import json
from os import stat

from urllib.parse import urlparse
from urllib.parse import unquote

from model.EventProcessor import EventProcessor

class PostMessageReceivedProcessor(EventProcessor):
    """ POSTMESSAGE RECEIVED
        -> hierarchy, href, hrefparts, receiver, sender, data, datatype,
        ports = [{channel_id, port_id}], targetorigincheck, sourceoriginaccessed = "yes"/"no"
    """

    def __init__(self, ctx, event):
        super().__init__(ctx, event)

        keyval = {
            "Receiver Origin Check": self.val["targetorigincheck"],
            "Data Type": self.val["datatype"],
            "Data": json.dumps(self.val["data"]),
            "Ports": json.dumps(self.val["ports"]),
            "Info": ""
        }
        color = None

        # Check if SSO-related params (like client_id, id_token, ...) are in postMessage data
        if self.search_loginreqresp(self.val["data"]):
            keyval["Info"] += (
                "Detected SSO-related parameter names in the postMessage data. Check if this "
                "postMessage is related to SSO. It may contain the Login Request or Login Response. "
            )
            color = "orange"

        # Check for wildcard receiver origin
        if self.val["targetorigincheck"] == "*":
            keyval["Info"] += (
                "Detected potential postMessage vulnerability. Check if this postMessage contains "
                "confidential data and is sent across windows. This postMessage does not "
                "guarantee message confidentiality, because the wildcard receiver origin check is used."
            )
            color = "red"

        else:

            # Check if receiver origin comes from user input
            related_events = self.search_userinput(ctx.processors, self.val["targetorigincheck"])
            
            if related_events:
                keyval["Info"] += (
                    "Detected that the postMessage receiver origin check potentially depends on "
                    "user input. Check if the user input in the related events influences the "
                    "postMessage receiver origin check by actively modifying it."
                )
                keyval["Related Events"] = ", ".join(str(processor.id) for processor in related_events)
                color = "orange"
            
            else:
                if not color: color = "green"

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
            keyval,
            color = color
        )

    @staticmethod
    def search_loginreqresp(data):
        """ Search for login request and login response in data.
            Returns true, if login request is potentially found.
            Returns false, if login request is potentially not found.
        """
        datastring = json.dumps(data)

        if (
            "client_id" in datastring
            or "redirect_uri" in datastring
            or "code" in datastring
            or "access_token" in datastring
            or "id_token" in datastring
        ):
            return True
        else:
            return False

    @staticmethod
    def search_userinput(processors, url):
        """ Search all events in reverse order that can contain user input for the url.
            Example: If "https://example.com" is used in postMessage or location set,
            then search all previous events that can contain user input as GET / POST
            parameters for this url. If some event like "Document Init" contains this url
            as GET parameter, we want to include this event as a related event to this event.

            Returns a list of related events (event processors).
        """
        related_events = []

        for processor in reversed(processors):
            
            # This is a GET request -> search for url in query & hash parameters
            # -> val["href"]
            if processor.key == "documentinit":
                if PostMessageReceivedProcessor.url_in_url(processor.val["href"], url):
                    related_events.append(processor)
            
            # This is a POST request -> search for url in query, hash, and body parameters
            # -> val["action"], val["form"]
            elif processor.key == "formsubmit":
                if PostMessageReceivedProcessor.url_in_url(processor.val["action"], url):
                    related_events.append(processor)

                if PostMessageReceivedProcessor.url_in_body(processor.val["form"], url):
                    related_events.append(processor)

        return related_events

    @staticmethod
    def url_in_url(base_url, search_url):
        """ Check if the "search_url" is contained in any query params or fragment of the "base_url" """
        parsed = urlparse(base_url)

        # Search "search_url" in query params of "base_url"
        if parsed.query:
            for query_param in parsed.query.split("&"):
                try:
                    key, val = query_param.split("=")
                    decoded_val = unquote(val)
                    if search_url in decoded_val:
                        return True
                except ValueError:
                    continue # this query pair does not contain any value

        # Search "search_url" in fragment of "base_url"
        if parsed.fragment:
            decoded_val = unquote(parsed.fragment)
            if search_url in decoded_val:
                return True

        return False

    @staticmethod
    def url_in_body(form, search_url):
        """ Check if the "search_url" is contained in any body param of a form """
        
        for val in form.values():
            if type(val) == str and search_url in val:
                return True
        
        return False
