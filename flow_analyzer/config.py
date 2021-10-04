import logging
import argparse
import os
import shutil

from distutils import dir_util
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from helpers import dir_path, parsed_url

logger = logging.getLogger(__name__)

""" Argparser """

def config_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url",
        type=parsed_url,
        required=True,
        help="set url to open in chrome"
    )
    parser.add_argument("-v", "--verbosity",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="DEBUG",
        help="set output verbosity"
    )
    parser.add_argument("-o", "--out",
        type=dir_path,
        required=True,
        help="set output directory"
    )
    parser.add_argument("-p", "--baseprofile",
        type=dir_path,
        required=True,
        help="set path to base chrome profile"
    )
    parser.add_argument("-c", "--cli",
        action="store_true",
        help="start command line interface tool"
    )
    return parser

""" Logging and Output """

def setup_outputdir(out, url, starttime):
    outputdir = f"{out}/{starttime}_{url.hostname}"
    try:
        os.mkdir(outputdir)
        logger.info(f"Output directory: '{outputdir}'")
        return outputdir
    except Exception as e:
        logger.error(f"Failed to create output directory: '{outputdir}'")
        logger.exception(e)
        raise(e)

def config_logger(outputdir, verbosity):
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    logformatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

    rootlogger = logging.getLogger()
    rootlogger.setLevel(log_levels[verbosity])

    logfile = f"{outputdir}/logs.log"
    filehandler = logging.FileHandler(logfile)
    filehandler.setFormatter(logformatter)
    rootlogger.addHandler(filehandler)

""" Chrome Profile """

def setup_chromeprofile(baseprofile):
    chromeprofile = "/tmp/chromeprofile_tmp"
    logger.info(f"Creating temporary chrome profile: '{chromeprofile}'")
    dir_util.copy_tree(baseprofile, chromeprofile)
    return chromeprofile

def destroy_chromeprofile(chromeprofile):
    logger.info(f"Deleting temporary chrome profile: '{chromeprofile}'")
    shutil.rmtree(chromeprofile)

""" Chrome Driver """

def config_chromedriver(chromeprofile):
    options = Options()
    options.add_argument("--ignore-certificate-errors") # for proxy support
    options.add_argument(
        f"--load-extension={os.getcwd()}/chrome_extensions/sso_frames,"
        f"{os.getcwd()}/chrome_extensions/disable_csp"
    )
    options.add_argument("--disable-web-security") # full access to cross-origin windows
    options.add_argument("--disable-site-isolation-trials") # access window.opener cross-origin
    options.add_argument(f"--user-data-dir={chromeprofile}") # cookies for idps
    driver = webdriver.Chrome(options=options)
    return driver
