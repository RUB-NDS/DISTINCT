#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import shutil
import threading

from time import sleep
from event.EventDispatcher import EventDispatcher
from event.EventHandler import EventHandler
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from distutils import dir_util

logger = logging.getLogger(__name__)

def config_argparser():
    """ Configure the argparser """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain",
        type=str,
        help="set domain to open in the new chrome instance"
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

    consolehandler = logging.StreamHandler(sys.stdout)
    consolehandler.setFormatter(logformatter)
    rootlogger.addHandler(consolehandler)


def setup_chromeprofile(baseprofile):
    chromeprofile = "{}/chromeprofile_tmp".format(os.getcwd())
    logger.info("Setup of temporary chrome profile in {}".format(chromeprofile))
    dir_util.copy_tree(baseprofile, chromeprofile)
    return chromeprofile


def destroy_chromeprofile(chromeprofile):
    logger.info("Cleanup of temporary chrome profile in {}".format(chromeprofile))
    shutil.rmtree(chromeprofile)


def config_chromedriver(chromeprofile):
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--load-extension={}/chrome_extension".format(os.getcwd()))
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--user-data-dir={}".format(chromeprofile))
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
        if args.domain:
            logger.info("Domain: https://{}".format(args.domain))
            driver.get("https://{}".format(args.domain))
        else:
            logger.info("Domain: about:blank".format(args.domain))
            driver.get("about:blank")
    except WebDriverException as e:
        logger.exception(e)
    
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
