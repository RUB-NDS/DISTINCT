#!/usr/bin/env python3

import logging
import os

from time import time
from selenium.common.exceptions import WebDriverException

from config import setup_outputdir
from config import config_argparser, config_logger
from config import setup_chromeprofile, config_chromedriver, destroy_chromeprofile
from event.EventDispatcher import EventDispatcher
from event.EventHandler import EventHandler
from cli.cli import CliPrompt

logger = logging.getLogger(__name__)

def main():
    # Setup argparser
    argparser = config_argparser()
    args = argparser.parse_args()
    
    # Setup global config variables
    starttime = str(int(time())) # UNIX timestamp
    outputdir = setup_outputdir(args.out, args.url, starttime)
    os.environ["STARTTIME"] = starttime
    os.environ["OUTPUTDIR"] = outputdir

    # Setup logger
    config_logger(outputdir, args.verbosity)

    # Setup event dispatcher and handler
    event_dispatcher = EventDispatcher()
    event_handler = EventHandler(event_dispatcher)
    event_handler.start()
    event_dispatcher.start()

    # Setup chromeprofile
    chromeprofile = setup_chromeprofile(args.baseprofile)

    # Setup chromedriver
    driver = config_chromedriver(chromeprofile)
    logger.info(f"Starting selenium: '{args.url.geturl()}'")
    try:
        driver.get(args.url.geturl())
    except WebDriverException as e:
        logger.exception(e)
        raise(e)
    
    if args.cli:
        """ Switch in CLI loop """
        cliprompt = CliPrompt(event_handler)
        cliprompt.cmdloop()
    else:
        """ Wait for threads to join """
        # Wait for KeyboardInterrupt to stop event dispatcher thread
        try:
            event_dispatcher.join()
        except KeyboardInterrupt as e:
            logger.info("Keyboard interrupt signal. Stopping the event dispatcher.")
        
        # Wait for KeyboardInterrupt to stop event handler thread
        try:
            event_handler.join()
        except KeyboardInterrupt as e:
            logger.info("Keyboard interrupt signal. Stopping the event handler.")

    # Cleanup
    destroy_chromeprofile(chromeprofile)

if __name__ == "__main__":
    main()
