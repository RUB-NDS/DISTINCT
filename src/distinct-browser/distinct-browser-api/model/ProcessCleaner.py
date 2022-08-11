from cgitb import handler
import logging
import os
import shutil
import base64
import time
from threading import Thread
from model.BrowserStatus import BrowserStatus
from model.ProxyStatus import ProxyStatus

logger = logging.getLogger(__name__)

class ProcessCleaner(Thread):

    def __init__(self, browser_api):
        logger.info("Initializing process cleaner thread")
        super(ProcessCleaner, self).__init__()

        self.browser_api = browser_api
        self.db = browser_api.db
        self.fs = browser_api.fs

    def run(self):
        logger.info("Starting process cleaner thread")

        while True:
            self.check_terminated_browsers()
            self.check_terminated_browsers_running_in_db()
            self.check_running_proxies_without_browser()
            self.check_terminated_proxies_running_in_db()
            time.sleep(5)

    """ Routines """

    def check_terminated_browsers(self):
        """ Detect and handle if there is a terminated browser that has not been
            terminated through the stop_browser method.
        """
        handlers_to_delete = []
        for uuid, process in self.browser_api.browsers_by_handler.items():
            if process.poll() is not None: # process terminated
                logger.warning(f"Browser for uuid {uuid} has been terminated manually!"
                " Use the \"Stop Browser\" button in the web interface instead.")
                logger.warning(f"Recovering from manually terminated browser ...")
                self.browser_api.stop_browser(uuid, expected_quit=False)
                handlers_to_delete.append(uuid)
        for uuid in handlers_to_delete:
            del self.browser_api.browsers_by_handler[uuid]

    def check_terminated_browsers_running_in_db(self):
        """ Detect and handle if browsers are running according to the database
            but not in the container. This can happen if the docker container
            is closed with the browser still running.
        """
        running_browsers = self.db["distinct"]["browsers"].find({
            "browser.status": BrowserStatus.RUNNING.value
        })
        for b in running_browsers:
            uuid = b["handler_uuid"]
            if uuid not in self.browser_api.browsers_by_handler:
                logger.warning(f"Browser for uuid {uuid} is running according to database"
                " although it is not running in the container!")
                logger.warning(f"Fixing database entry and restoring files ...")

                self.browser_api.destroy_chrome_extensions(uuid) # cleanup

                # Encode the profile in zip
                profile_zip_b64 = None
                profile_path = f"/app/data/chrome-profiles/chrome-profile_{uuid}"
                profile_zip_path = f"/app/data/chrome-profiles/chrome-profile_{uuid}.zip"
                if os.path.isfile(profile_zip_path):
                    os.remove(profile_zip_path)
                if os.path.exists(profile_path):
                    shutil.make_archive(profile_path, "zip", profile_path)
                    with open(profile_zip_path, "rb") as f:
                        profile_zip_bytes = f.read()
                        profile_zip_b64 = base64.b64encode(profile_zip_bytes)

                # Cleanup profile
                if os.path.isfile(profile_zip_path):
                    os.remove(profile_zip_path)
                if os.path.exists(profile_path):
                    shutil.rmtree(profile_path)

                # Update browser in database
                if profile_zip_b64:
                    profile_fs = self.fs.put(profile_zip_b64)
                else:
                    profile_fs = None
                self.db["distinct"]["browsers"].update_one(
                    {"handler_uuid": uuid},
                    {"$set": {
                        "browser.returncode": -1, # we have to guess return code
                        "browser.status": BrowserStatus.STOPPED.value,
                        "browser.endtime": str(int(time.time())),
                        "browser.profile": str(profile_fs) if profile_fs else None
                    }}
                )

    def check_running_proxies_without_browser(self):
        """ Check and handle if there are running proxies without a browser """
        proxies_to_delete = []
        for uuid, process in self.browser_api.proxies_by_handler.items():
            if (
                process.poll() is None # process is running
                and (
                    (uuid not in self.browser_api.browsers_by_handler) # no browser
                    or (
                        uuid in self.browser_api.browsers_by_handler
                        and self.browser_api.browsers_by_handler[uuid].poll() is not None
                    ) # browser terminated
                )
            ):
                logger.warning(f"Proxy for uuid {uuid} is running although browser terminated!")
                logger.warning(f"Terminating proxy as well ...")
                self.browser_api.stop_proxy(uuid, expected_quit=False)
                proxies_to_delete.append(uuid)
        for uuid in proxies_to_delete:
            del self.browser_api.proxies_by_handler[uuid]

    def check_terminated_proxies_running_in_db(self):
        """ Detect and handle if proxies are running according to the database
            but not in the container. This can happen if the docker container
            is closed with the proxy still running.
        """
        running_proxies = self.db["distinct"]["proxies"].find({
            "proxy.status": ProxyStatus.RUNNING.value
        })
        for b in running_proxies:
            uuid = b["handler_uuid"]
            if uuid not in self.browser_api.proxies_by_handler:
                logger.warning(f"Proxy for uuid {uuid} is running according to database"
                " although it is not running in the container!")
                logger.warning(f"Fixing database entry and restoring files ...")

                stream_path = f"/app/data/chrome-proxy/proxy-stream_{uuid}.dump"
                har_path = f"/app/data/chrome-proxy/proxy-hardump_{uuid}.har"

                # Encode the STREAM file
                stream_b64 = None
                if os.path.exists(stream_path):
                    with open(stream_path, "rb") as f:
                        stream_bytes = f.read()
                        stream_b64 = base64.b64encode(stream_bytes)

                # Encode the HAR file
                har_b64 = None
                if os.path.exists(har_path):
                    with open(har_path, "rb") as f:
                        har_bytes = f.read()
                        har_b64 = base64.b64encode(har_bytes)

                # Cleanup STREAM and HAR
                if os.path.isfile(stream_path):
                    os.remove(stream_path)
                if os.path.isfile(har_path):
                    os.remove(har_path)

                # Update proxy in database
                if stream_b64:
                    stream_fs = self.fs.put(stream_b64)
                else:
                    stream_fs = None
                if har_b64:
                    har_fs = self.fs.put(har_b64)
                else:
                    har_fs = None
                self.db["distinct"]["proxies"].update_one(
                    {"handler_uuid": uuid},
                    {"$set": {
                        "proxy.returncode": -1, # we have to guess return code
                        "proxy.status": ProxyStatus.STOPPED.value,
                        "proxy.endtime": str(int(time.time())),
                        "proxy.stream": str(stream_fs) if stream_fs else None,
                        "proxy.hardump": str(har_fs) if har_fs else None
                    }}
                )
