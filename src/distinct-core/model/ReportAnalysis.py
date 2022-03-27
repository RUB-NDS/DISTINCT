import json
import logging

from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

class ReportAnalysis:

    @staticmethod
    def url_in_query_or_fragment(base_url, search_url):
        """ Check if search_url is contained in query or fragment of base_url.
            Returns:
                - True, if search_url is contained in base_url
                - False, if search_url is not contained in base_url
        """
        base_url_parsed = urlparse(base_url)

        # Search search_url in query of base_url
        if base_url_parsed.query:
            for query_param in base_url_parsed.query.split("&"):
                try:
                    key, val = query_param.split("=")
                    decoded_val = unquote(val)
                    if search_url in decoded_val:
                        return True
                except ValueError:
                    continue # this query pair does not contain any value

        # Search search_url in fragment of base_url
        if base_url_parsed.fragment:
            decoded_val = unquote(base_url_parsed.fragment)
            if search_url in decoded_val:
                return True

        return False

    @staticmethod
    def url_in_body(form, search_url):
        """ Check if search_url is contained in body parameters of form.
            Returns:
                - True, if search_url is contained in form
                - False, if search_url is not contained in form
        """

        for val in form.values():
            if type(val) == str and search_url in val:
                return True

        return False

    @staticmethod
    def sso_params_in_object(data_object):
        """ Search for SSO parameters in given object.
            Returns:
                - True, if SSO parameters are found
                - False, if SSO parameters are not found
        """
        data_string = json.dumps(data_object)

        if (
            "client_id" in data_string
            or "redirect_uri" in data_string
            or "code" in data_string
            or "access_token" in data_string
            or "id_token" in data_string
        ):
            return True
        else:
            return False

    @staticmethod
    def related_reports_with_url_in_user_input(reports, url):
        """ Search all reports in reverse order for the url.
            Returns:
                - List of related reports with url in user input
        """
        related_reports = []

        for report in reversed(reports):
            logger.debug(f"Check if report #{report['id']} contains user input with '{url}'")

            # This is a GET request -> search for url in query and fragment
            if report["key"] == "documentinit":
                logger.debug(f"Found documentinit report: Check if '{url}' is in GET parameters")
                if ReportAnalysis.url_in_query_or_fragment(report["val"]["href"], url):
                    logger.debug(f"Found related report: {report['id']}")
                    related_reports.append(report)

            # This is a POST request -> search for url in query, fragment, and body
            elif report["key"] == "formsubmit":
                logger.debug(f"Found formsubmit report: Check if '{url}' is in GET or POST parameters")
                if ReportAnalysis.url_in_query_or_fragment(report["val"]["action"], url):
                    logger.debug(f"Found related report: {report['id']}")
                    related_reports.append(report)

                if ReportAnalysis.url_in_body(report["val"]["form"], url):
                    logger.debug(f"Found related report: {report['id']}")
                    related_reports.append(report)

        return related_reports

    @staticmethod
    def location_target_is_relative_redirect(property, target):
        """ Check if the target of the location set event is a relative redirect.
            Returns:
                - True, if target is a relative redirect
                - False, if target is not a relative redirect
        """

        # If location set via href, assign, or replace, and starts with "/", it is relative redirect
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
