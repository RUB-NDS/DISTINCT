import json
import logging
import re
from model.ReportProcessor import ReportProcessor

logger = logging.getLogger(__name__)

class AddEventListenerProcessor(ReportProcessor):
    """ ADD EVENT LISTENER
        -> hierarchy, href, hrefparts, type, method, callback
    """

    def __init__(self, ctx, report):
        super().__init__(ctx, report)

        self.check_origin_keyword()
        self.check_origin_equal_cmp()

        ctx.sequencediagram.note(
            self.val["hierarchy"],
            self.id,
            self.timestamp,
            "Add Event Listener",
            {
                "Type": self.val["type"],
                "Method": self.val["method"],
                "Callback": json.dumps(self.val["callback"])
            }
        )

    def check_origin_keyword(self):
        """ Check if the origin keyword is present in the callback. """
        logger.debug(f"Checking if 'origin' keyword is in callback of report #{self.id}")
        if "origin" in self.report["val"]["callback"]:
            self.report["val"]["origin_in_callback"] = True
        else:
            self.report["val"]["origin_in_callback"] = False

    def check_origin_equal_cmp(self):
        """ Check if the origin is used in an equal comparison """
        logger.debug(f"Checking if 'origin' is used in an equal comparison of report #{self.id}")
        cmp_types = {
            "origin_equals_string": [
                "\.origin" + "\s*===?\s*" + "'[^']+'",
                '\.origin' + '\s*===?\s*' + '"[^"]+"',
                "'[^']+'" + "\s*===?\s*" + "[\w\.]+\.origin",
                '"[^"]+"' + '\s*===?\s*' + '[\w\.]+\.origin'
            ],
            "origin_equals_variable": [
                "\.origin" + "\s*===?\s*" + "[\w\.]+",
                "[\w\.]+" + "\s*===?\s*" + "[\w\.]+\.origin",
            ],
            "origin_equals_origin": [
                "\.origin" + "\s*===?\s*" + "[\w\.]+\.origin",
            ],
            "origin_equals_window_origin": [
                "\.origin" + "\s*===?\s*" + "window\.origin",
                "window\.origin" + "\s*===?\s*" + "[\w\.]+\.origin",
            ],
            "origin_equals_location_origin": [
                "\.origin" + "\s*===?\s*" + "window\.location\.origin",
                "window\.location\.origin" + "\s*===?\s*" + "[\w\.]+\.origin",
                "\.origin" + "\s*===?\s*" + "window\.document\.location\.origin",
                "window\.document\.location\.origin" + "\s*===?\s*" + "[\w\.]+\.origin",
                "\.origin" + "\s*===?\s*" + "document\.location\.origin",
                "document\.location\.origin" + "\s*===?\s*" + "[\w\.]+\.origin",
                "\.origin" + "\s*===?\s*" + "location\.origin",
                "location\.origin" + "\s*===?\s*" + "[\w\.]+\.origin",
            ]
        }
        for cmp_type, cmp_regexes in cmp_types.items():
            self.report["val"][cmp_type] = False
            for cmp_regex in cmp_regexes:
                if re.search(cmp_regex, self.report["val"]["callback"]):
                    logger.debug(f"Found {cmp_type} in callback of report #{self.id}")
                    self.report["val"][cmp_type] = True
