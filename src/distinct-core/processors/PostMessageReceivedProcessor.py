import json
import logging

from urllib.parse import urlparse
from urllib.parse import unquote

from model.ReportProcessor import ReportProcessor

logger = logging.getLogger(__name__)

class PostMessageReceivedProcessor(ReportProcessor):
    """ POSTMESSAGE RECEIVED
        -> hierarchy, href, hrefparts, target_frame, source_frame, data, data_type,
        ports = [{channel_id, port_id}], target_origin_check, source_origin_accessed = true|false
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)
        logger.debug(f"Initializing PostMessageReceivedProcessor for report #{self.id}")

        keyval = {
            "Receiver Origin Check": self.val["target_origin_check"],
            "Data Type": self.val["data_type"],
            "Data": json.dumps(self.val["data"]),
            "Ports": json.dumps(self.val["ports"]),
            "Info": ""
        }
        color = None

        # Check if SSO-related params (like client_id, id_token, ...) are in postMessage data
        logger.debug(f"Check if postMessage data in report #{self.id} contains SSO-related parameters")
        if self.search_loginreqresp(self.val["data"]):
            report["val"]["sso_params"] = True
            keyval["Info"] += (
                "Detected SSO-related parameter names in the postMessage data. Check if this "
                "postMessage is related to SSO. It may contain the Login Request or Login Response. "
            )
            color = "orange"
        else:
            report["val"]["sso_params"] = False

        # Check for wildcard receiver origin
        logger.debug(f"Check if postMessage in report #{self.id} uses wildcard receiver origin")
        if self.val["target_origin_check"] == "*":
            keyval["Info"] += (
                "Detected potential postMessage vulnerability. Check if this postMessage contains "
                "confidential data and is sent across windows. This postMessage does not "
                "guarantee message confidentiality, because the wildcard receiver origin check is used."
            )
            color = "red"

        else:

            # Bottom Up: Check if receiver origin comes from user input
            logger.debug(f"Check if postMessage receiver origin in report #{self.id} comes from user input")
            related_reports = self.search_userinput(ctx.reports, self.val["target_origin_check"])

            if related_reports:
                report["val"]["related_reports"] = ", ".join(str(report["id"]) for report in related_reports)
                keyval["Related Reports"] = ", ".join(str(report["id"]) for report in related_reports)
                keyval["Info"] += (
                    "Detected that the postMessage receiver origin check potentially depends on "
                    "user input. Check if the user input in the related events influences the "
                    "postMessage receiver origin check by actively modifying it."
                )
                color = "orange"
            else:
                report["val"]["related_reports"] = ""
                if not color: color = "green"

        ctx.sequencediagram.arrow(
            self.val["source_frame"],
            self.val["target_frame"],
            "PostMessage Received"
        )

        ctx.sequencediagram.note(
            self.val["target_frame"],
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
    def search_userinput(reports, url):
        """ Search all reports in reverse order that can contain user input for the url.
            Example: If "https://example.com" is used in postMessage or location set,
            then search all previous events that can contain user input as GET / POST
            parameters for this url. If some report like "Document Init" contains this url
            as GET parameter, we want to include this report as a related report to this report.

            Returns a list of related reports.
        """
        related_reports = []

        for report in reversed(reports):
            logger.debug(f"Checking if report #{report['id']} contains user input for {url}")

            # This is a GET request -> search for url in query & hash parameters
            # -> val["href"]
            if report["key"] == "documentinit":
                logger.debug(f"Found documentinit report: Check if '{url}' is in GET parameters")
                if PostMessageReceivedProcessor.url_in_url(report["val"]["href"], url):
                    logger.debug(f"Found related event: {report['id']}")
                    related_reports.append(report)

            # This is a POST request -> search for url in query, hash, and body parameters
            # -> val["action"], val["form"]
            elif report["key"] == "formsubmit":
                logger.debug(f"Found formsubmit report: Check if '{url}' is in GET or POST parameters")
                if PostMessageReceivedProcessor.url_in_url(report["val"]["action"], url):
                    logger.debug(f"Found related event: {report['id']}")
                    related_reports.append(report)

                if PostMessageReceivedProcessor.url_in_body(report["val"]["form"], url):
                    logger.debug(f"Found related event: {report['id']}")
                    related_reports.append(report)

        return related_reports

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
