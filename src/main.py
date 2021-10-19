#!/usr/bin/env python3

import logging
import os

from time import time
from selenium.common.exceptions import WebDriverException

from config import setup_outputdir, setup_argparser, setup_logger
from config import setup_chromeprofile, setup_chromedriver
from config import setup_proxy, set_all_cookies
from event.EventDispatcher import EventDispatcher
from event.EventHandler import EventHandler
from cli import CliPrompt

logger = logging.getLogger(__name__)

def main():
    # Setup argparser
    argparser = setup_argparser()
    args = argparser.parse_args()
    
    # Setup global config variables
    url = args.url.geturl()
    starttime = str(int(time())) # UNIX timestamp
    outputdir = setup_outputdir(args.out, args.url, starttime)
    os.environ["URL"] = url
    os.environ["STARTTIME"] = starttime
    os.environ["OUTPUTDIR"] = outputdir

    # Setup logger
    setup_logger(outputdir, args.verbosity)

    # Setup intercepting proxy
    proxy = setup_proxy(outputdir, args.port_proxy)

    # Setup event dispatcher and handler threads
    event_dispatcher = EventDispatcher()
    event_handler = EventHandler(event_dispatcher)
    event_handler.start()
    event_dispatcher.start()

    # Setup chromeprofile
    chromeprofile = setup_chromeprofile(outputdir)

    # Setup chromedriver
    driver = setup_chromedriver(chromeprofile, args.port_proxy, args.chromium_path, args.webdriver_path)

    # Setup cookies
    if args.cookie_file:
        set_all_cookies(driver, args.cookie_file)

    # Load URL
    logger.info(f"URL: {url}")
    try:
        driver.get(url)
    except WebDriverException as e:
        logger.exception(e)
    
    # Switch in CLI loop
    cliprompt = CliPrompt(driver, proxy, outputdir, chromeprofile, event_handler)
    cliprompt.cmdloop()

if __name__ == "__main__":
    main()
