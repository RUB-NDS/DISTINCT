#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import shutil

from time import time
from event.EventDispatcher import EventDispatcher
from event.EventHandler import EventHandler
from cli.cli import CliPrompt
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from distutils import dir_util

logger = logging.getLogger(__name__)

def config_argparser():
    """ Configure the argparser """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url",
        type=str,
        help="set URL to open in the new chrome instance"
    )
    parser.add_argument("-v", "--verbosity",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="DEBUG",
        help="set output verbosity"
    )
    parser.add_argument("-l", "--logfile",
        type=str,
        help="set path to logfile"
    )
    parser.add_argument("-p", "--baseprofile",
        type=str,
        required=True,
        help="set path to base chromeprofile with cookies for idps"
    )
    parser.add_argument("-c", "--cli",
        action="store_true",
        help="start command line interface tool"
    )
    return parser


def config_logger(args):
    """ Configure the logger """
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    logformatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

    rootlogger = logging.getLogger()
    rootlogger.setLevel(log_levels[args.verbosity])
    
    if args.logfile:
        filehandler = logging.FileHandler("{}".format(args.logfile))
        filehandler.setFormatter(logformatter)
        rootlogger.addHandler(filehandler)

    if args.cli:
        if not args.logfile:
            # Use default logfile
            args.logfile = "{}/logs/{}.log".format(os.getcwd(), int(time()))
            filehandler = logging.FileHandler(args.logfile)
            filehandler.setFormatter(logformatter)
            rootlogger.addHandler(filehandler)
    else:
        consolehandler = logging.StreamHandler(sys.stdout)
        consolehandler.setFormatter(logformatter)
        rootlogger.addHandler(consolehandler)


def setup_chromeprofile(baseprofile):
    chromeprofile = "/tmp/chromeprofile_tmp"
    logger.info("Setup of temporary chrome profile in {}".format(chromeprofile))
    dir_util.copy_tree(baseprofile, chromeprofile)
    return chromeprofile


def destroy_chromeprofile(chromeprofile):
    logger.info("Cleanup of temporary chrome profile in {}".format(chromeprofile))
    shutil.rmtree(chromeprofile)


def config_chromedriver(chromeprofile):
    options = Options()
    options.add_argument("--ignore-certificate-errors") # for proxy support
    options.add_argument(
        "--load-extension={}/chrome_extensions/sso_frames,{}/chrome_extensions/disable_csp".format(
            os.getcwd(), os.getcwd()
        )
    )
    options.add_argument("--disable-web-security") # full access to cross-origin windows
    options.add_argument("--disable-site-isolation-trials") # access window.opener cross-origin
    options.add_argument("--user-data-dir={}".format(chromeprofile)) # cookies for idps
    driver = webdriver.Chrome(options=options)
    return driver


def main():
    # Setup argparser
    argparser = config_argparser()
    args = argparser.parse_args()
    
    # Setup logger
    config_logger(args)

    # Setup event dispatcher and handler
    event_dispatcher = EventDispatcher()
    event_handler = EventHandler(event_dispatcher)
    
    event_handler.start()
    event_dispatcher.start()

    # Setup chromeprofile
    chromeprofile = setup_chromeprofile(args.baseprofile)

    # Setup chromedriver
    driver = config_chromedriver(chromeprofile)
    logger.info("Starting selenium chromedriver")
    try:
        if args.url:
            logger.info("URL: {}".format(args.url))
            driver.get(args.url)
        else:
            logger.info("URL: about:blank")
            driver.get("about:blank")
    except WebDriverException as e:
        logger.exception(e)
    
    if args.cli:
        """ SWITCH IN CLI LOOP """
        cliprompt = CliPrompt(event_handler)
        cliprompt.cmdloop()
    else:
        """ WAIT FOR THREADS TO JOIN """
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
