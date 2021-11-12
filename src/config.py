import logging
import argparse
import os
import subprocess
import json
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium_stealth import stealth

logger = logging.getLogger(__name__)

""" Argparser """

def setup_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url",
        type=parsed_url,
        required=True,
        help="set url to open in browser"
    )
    parser.add_argument("-o", "--out",
        type=dir_path,
        required=True,
        help="set output directory"
    )
    parser.add_argument("-c", "--cookie-file",
        type=file_path,
        help="set path to cookie file"
    )
    parser.add_argument("--verbosity",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="DEBUG",
        help="set output verbosity"
    )
    parser.add_argument("--chromium-path",
        type=file_path,
        help="set path to chrome / chromium binary"
    )
    parser.add_argument("--webdriver-path",
        type=file_path,
        help="set path to chrome / chromium webdriver binary"
    )
    parser.add_argument("--port-proxy",
        type=int,
        default=20201,
        help="set port of proxy"
    )
    return parser

def file_path(string):
    """ Check if file exists and return absolute path """
    if os.path.isfile(string):
        return os.path.abspath(string)
    else:
        raise FileNotFoundError(string)

def dir_path(string):
    """ Check if directory exists and return absolute path """
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)

def parsed_url(url):
    """ Return parsed URL """
    return urllib.parse.urlparse(url)

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

def setup_logger(outputdir, verbosity):
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

def code_version():
    """ Return the version of the current git checkout """
    version = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return version

""" Chrome Profile """

def setup_chromeprofile(outputdir):
    chromeprofile = f"{outputdir}/chromeprofile"
    logger.info(f"Creating chrome profile: {chromeprofile}")
    return chromeprofile

def set_all_cookies(driver, cookiefile):
    """ Load all cookies into browser """
    with open(cookiefile, "r") as f:
        cookies = json.load(f)
        driver.execute_cdp_cmd("Network.setCookies", cookies)
        logger.info(f"Loaded all cookies into browser: {cookiefile}")

def store_all_cookies(driver, outputdir):
    """ Store all browser cookies in output directory
    {
        'name': 'Cookie',
        'size': 4,
        'value': 'test',
        'domain': '.foo.com',
        'expires': 1649241526.721609,
        'httpOnly': True,
        'path': '/',
        'priority': 'Medium',
        'sameParty': False,
        'sameSite': 'None',
        'secure': True,
        'session': False,
        'sourcePort': 443,
        'sourceScheme': 'Secure',
    }
    """
    cookies = driver.execute_cdp_cmd("Network.getAllCookies", {}) # {"cookies": [{...}, ...]}
    cookiefile = f"{outputdir}/cookiejar.json"
    with open(cookiefile, "w+") as f:
        json.dump(cookies, f)
        logger.info(f"Saved all browser cookies: {cookiefile}")

""" Chrome Driver """

def setup_chromedriver(chromeprofile, proxyport, chromium_binary=None, webdriver_path=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors") # for proxy support
    options.add_argument("--load-extension=./chrome_extension") # generates in-browser events
    options.add_argument("--disable-web-security") # full access to cross-origin windows
    options.add_argument("--disable-site-isolation-trials") # access window.opener cross-origin
    options.add_argument(f"--user-data-dir={chromeprofile}") # cookies for idps
    options.add_argument('--disable-features=MediaRouter') # avoid "accept incoming network connections?"
    options.add_argument("--disable-http2") # for proxy support
    options.add_argument("start-maximized") # bypass selenium detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # bypass selenium detection
    options.add_experimental_option("useAutomationExtension", False)  # bypass selenium detection
    
    if chromium_binary:
        options.binary_location = chromium_binary

    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = f"127.0.0.1:{proxyport}"
    proxy.ssl_proxy = f"127.0.0.1:{proxyport}"
    capabilities = webdriver.DesiredCapabilities.CHROME
    proxy.add_to_capabilities(capabilities)
    
    if webdriver_path:
        driver = webdriver.Chrome(
            executable_path=webdriver_path,
            options=options,
            desired_capabilities=capabilities
        )
    else:
        driver = webdriver.Chrome(
            options=options,
            desired_capabilities=capabilities
        )

    # Bypass selenium detection
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True
    )
    
    return driver

""" Proxy """

def setup_proxy(outputdir, proxyport):
    stdout = f"{outputdir}/proxy_stdout.log"
    stderr = f"{outputdir}/proxy_stderr.log"
    
    with open(stdout, "wb") as out, open(stderr, "wb") as err:
        proxy = subprocess.Popen([
            "mitmdump",
            "--listen-host", "127.0.0.1",
            "--listen-port", str(proxyport),
            "--save-stream-file", f"{outputdir}/proxy.dump",
            "--quiet",
            "--scripts", "./mitmproxy/har.py", # Export HARs
            "--scripts", "./mitmproxy/redirects.py", # Transform HTTP/3** redirects to HTTP/200 docs
            "--set", f"hardump={outputdir}/proxy.har"
        ], stdout=out, stderr=err)
    
        logger.info(f"Started proxy on port {proxyport}")
        
        return proxy

def terminate_proxy(proxy):
    logger.info("Terminating proxy")
    proxy.terminate()
