import logging

from urllib.parse import urlparse

from model.ReportProcessor import ReportProcessor
from model.ReportAnalysis import ReportAnalysis
from processors.PostMessageReceivedProcessor import PostMessageReceivedProcessor

logger = logging.getLogger(__name__)

class LocationSetProcessor(ReportProcessor):
    """ LOCATION SET
        -> hierarchy, href, hrefparts, prop, target
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        seq_diag_keyval = {
            "Property": self.val["prop"],
            "Target": self.val["target"]
        }
        color = None

        # 1) Check for relative redirects
        logger.debug(f"Check if location set in report #{self.id} is relative redirect")
        if ReportAnalysis.location_target_is_relative_redirect(self.val["prop"], self.val["target"]):
            report["val"]["relative_redirect"] = True
            seq_diag_keyval["Info"] = (
                "Detected potential relative redirect. Check if this redirect contains "
                "confidential data and is performed across windows."
            )
            color="orange"
        else:
            report["val"]["relative_redirect"] = False

            # 2) If it is not a relative redirect, check if redirect target comes from user input
            logger.debug(f"Check if location set in report #{self.id} comes from user input")
            related_reports = []

            # If the location is set with a method that can (1) change its origin
            # and (2) include confidential data in query or fragment
            if (
                self.val["prop"] == "href"
                or self.val["prop"] == "assign"
                or self.val["prop"] == "replace"
            ):
                target_parsed = urlparse(self.val["target"])
                search_url = ""
                if target_parsed.scheme: search_url += f"{target_parsed.scheme}://"
                if target_parsed.netloc: search_url += target_parsed.netloc
                if target_parsed.path: search_url += target_parsed.path
                # We do not want to search for query or fragment

                if search_url:
                    related_reports = ReportAnalysis.related_reports_with_url_in_user_input(ctx.reports, search_url)

            related = ", ".join(str(report["id"]) for report in related_reports)
            report["val"]["related_reports"] = related
            logger.debug(f"Related reports: {related}")

            if related_reports:
                seq_diag_keyval["Info"] = (
                    "Detected that the redirect target potentially depends on "
                    "user input. Check if the user input in the related events influences the "
                    "redirect target by actively modifying it."
                )
                seq_diag_keyval["Related Events"] = related
                color = "orange"
            else:
                color = "green"

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Location Set",
            seq_diag_keyval,
            color = color
        )
