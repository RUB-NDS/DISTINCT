#!/usr/bin/env python3

import logging
import json

from time import time
from selenium.common.exceptions import WebDriverException

from config import setup_outputdir, setup_argparser, setup_logger, code_version
from config import setup_chromeprofile, setup_chromedriver
from config import setup_proxy, set_all_cookies
from config import terminate_proxy, store_all_cookies
from model.EventDispatcher import EventDispatcher
from model.EventHandler import EventHandler

logger = logging.getLogger(__name__)

def main():
    # Setup argparser
    argparser = setup_argparser()
    args = argparser.parse_args()
    
    # Setup config
    url = args.url.geturl()
    starttime = str(int(time())) # UNIX timestamp
    outputdir = setup_outputdir(args.out, args.url, starttime)
    codeversion = code_version()

    # Setup logger
    setup_logger(outputdir, args.verbosity)

    # Setup intercepting proxy
    proxy = setup_proxy(outputdir, args.port_proxy)

    # Setup event dispatcher and handler threads
    event_dispatcher = EventDispatcher()
    event_handler = EventHandler(event_dispatcher, {
        "url": url,
        "starttime": starttime,
        "outputdir": outputdir,
        "codeversion": codeversion
    })
    event_handler.start()
    event_dispatcher.start()

    # Setup chromeprofile
    chromeprofile = setup_chromeprofile(outputdir)

    # Setup chromedriver
    driver = setup_chromedriver(
        chromeprofile,
        args.port_proxy,
        args.chromium_path,
        args.webdriver_path
    )

    # Setup cookies
    if args.cookie_file:
        set_all_cookies(driver, args.cookie_file)

    # Load URL
    logger.info(f"URL: {url}")
    print(f"[+] URL: {url}")
    try:
        driver.get(url)
    except WebDriverException as e:
        logger.exception(e)
        print(e)
    else:
        # Wait for user to log in with SSO
        input("[+] Log in with Single Sign-On and press ENTER once logged in")
    
    print("[+] Shutting down ...")

    # Terminate the proxy
    terminate_proxy(proxy)

    # Store all browser cookies in file
    store_all_cookies(driver, outputdir)

    # Store event history
    historyfile = f"{outputdir}/history.json"
    with open(historyfile, "w+") as f:
        json.dump(event_handler.execution_context.history, f)
        logger.info(f"Saved event history: {historyfile}")

    # Store event report
    reportfile = f"{outputdir}/report.json"
    with open(reportfile, "w+") as f:
        json.dump(event_handler.execution_context.reports, f)
        logger.info(f"Saved event reports: {reportfile}")

    # Compile plantuml sequence diagram to svg
    event_handler.execution_context.sequencediagram.compile()

if __name__ == "__main__":
    main()
