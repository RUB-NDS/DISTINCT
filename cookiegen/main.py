#!/usr/bin/env python3

import argparse
import json

from time import sleep
from selenium import webdriver
from selenium_stealth import stealth

def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output",
        type=str,
        required=True,
        help="set output file for cookies"
    )
    args = parser.parse_args()

    # Setup webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    # Bypass selenium detection
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # Open Google's account page for signin
    # and wait for interrupt signal from user hitting CTRL+C
    print("[+] Loading Google's signin page ...")
    try:
        driver.get("https://accounts.google.com")
        print("[+] Please sign into Google and hit CTRL+C when finished")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

    # Open Facebook's account page for signin
    # and wait for interrupt signal from user hitting CTRL+C
    print("[+] Loading Facebook's signin page ...")
    try:
        driver.get("https://www.facebook.com")
        print("[+] Please sign into Facebook and hit CTRL+C when finished")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

    # Retrieve all browser cookies
    cookies = driver.execute_cdp_cmd("Network.getAllCookies", {})
    with open(args.output, "w+") as f:
        json.dump(cookies, f)
        print(f"Saved all browser cookies in {args.output}")
    
    driver.quit()

if __name__ == "__main__":
    main()
