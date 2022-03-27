import json
import logging

from model.ReportProcessor import ReportProcessor
from model.BottomUpAnalysis import BottomUpAnalysis

logger = logging.getLogger(__name__)

class PostMessageReceivedProcessor(ReportProcessor):
    """ POSTMESSAGE RECEIVED
        -> hierarchy, href, hrefparts, target_frame, source_frame, data, data_type,
        ports = [{channel_id, port_id}], target_origin_check, source_origin_accessed = true|false
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        seq_diag_keyval = {
            "Receiver Origin Check": self.val["target_origin_check"],
            "Data Type": self.val["data_type"],
            "Data": json.dumps(self.val["data"]),
            "Ports": json.dumps(self.val["ports"]),
            "Info": ""
        }
        color = None

        # Check if postMessage data contains SSO parameters
        logger.debug(f"Check if postMessage data in report #{self.id} contains SSO parameters")
        if BottomUpAnalysis.sso_params_in_object(self.val["data"]):
            report["val"]["sso_params"] = True
            seq_diag_keyval["Info"] += (
                "Detected SSO-related parameter names in the postMessage data. Check if this "
                "postMessage is related to SSO. It may contain the Login Request or Login Response. "
            )
            color = "orange"
        else:
            report["val"]["sso_params"] = False

        # Check if postMessage receiver origin check is wildcard
        logger.debug(f"Check if postMessage in report #{self.id} uses wildcard receiver origin")
        if self.val["target_origin_check"] == "*":
            seq_diag_keyval["Info"] += (
                "Detected potential postMessage vulnerability. Check if this postMessage contains "
                "confidential data and is sent across windows. This postMessage does not "
                "guarantee message confidentiality, because the wildcard receiver origin check is used."
            )
            color = "red"
        else:

            # Check if postMessage receiver origin comes from user input
            logger.debug(f"Check if postMessage receiver origin in report #{self.id} comes from user input")
            related_reports = BottomUpAnalysis.related_reports_with_url_in_user_input(ctx.reports, self.val["target_origin_check"])
            if related_reports:
                related = ", ".join(str(report["id"]) for report in related_reports)
                report["val"]["related_reports"] = related
                seq_diag_keyval["Related Reports"] = related
                seq_diag_keyval["Info"] += (
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
            seq_diag_keyval,
            color = color
        )
