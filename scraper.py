# Imports
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import time
from configparser import ConfigParser
import argparse

import logging
from typing import List, Any

from LinkedInScraper import LinkedinScraper


# Functions and Classes


def quit_driver(driver):
    logging.critical("Quitting...")
    driver.quit()


def get_selenium_drivers(running: bool, **kwargs) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1920,1080")

    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")

    if running:
        portnumber = kwargs.get("portnumber", 9222)
        options.add_experimental_option("debuggerAddress", f"localhost:{portnumber}")
    else:
        options.add_experimental_option("detach", True)

    options.add_argument("--disable-logging")
    service = Service("/usr/local/bin/chromedriver")
    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logging.exception(e)
        logging.critical("driver failed to start...")
        quit_driver(driver)
        exit(1)

    logging.debug("waiting for the drivers to start...")
    time.sleep(2)
    return driver


def sign_in(url: str, driver: object, username: str, password: str) -> None:
    logging.debug("Starting to load the page...")
    driver.get(url)
    time.sleep(3)
    logging.debug("Page loaded...")

    logging.debug("signing in...")

    username_input_box = driver.find_element(By.ID, value="session_key")
    username_input_box.send_keys(username)
    time.sleep(0.5)

    password_input_box = driver.find_element(By.ID, value="session_password")
    password_input_box.send_keys(password)
    time.sleep(0.5)

    try:
        btn = driver.find_element(
            By.CLASS_NAME, value="sign-in-form__submit-btn--full-width"
        )
        btn.click()
        time.sleep(10)
        print("signed in...")
    except Exception as e:
        logging.exception(e)
        logging.critical(
            "Not able to sign in... please check your credentials... or linkedin sign in page with authenication is opening... try using --running flag"
        )

def parse_urls_from_filepath(path: str) -> List[str]:
    try:
        with open(path, "r") as f:
            urls = f.readlines()
        urls = [url.strip() for url in urls]
        return urls
    except Exception as e:
        logging.exception(e)
        logging.critical("Error while reading the file...")
        exit(1)

def extract_profile_information(url: str, driver: object, save: bool) -> None:
    ### GETTING PROFILE ###
    profile_url = url
    page_source = get_profile(driver, profile_url)
    ### PROFILE ACQUIRED ###

    ### EXTRACTING INFORMATION ###
    time.sleep(2)
    extractor = LinkedinScraper(page_source, driver, args.save)

    if args.save:
        extractor.save_output_in_file()
    else:
        print(extractor.output)

    ### INFORMATION EXTRACTED ###


def get_profile(driver: Any, url: str) -> str:
    if driver.current_url != url:
        logging.debug("getting profile...")

        driver.get(url)
        time.sleep(3)

        logging.debug("profile loaded...")
    else:
        logging.debug("profile already loaded...")

    profile = driver.page_source
    return profile


if __name__ == "__main__":
    ### PARSING ARGUMENTS ##
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--path",
        type=str,
        help="Path to the file containing URL's in .txt format",
        default=None,
    )
    group.add_argument(
        "--url",
        type=str,
        help="URL of the LinkedIn profile to scrape",
        default="https://www.linkedin.com/in/kshivendu/",
    )

    parser.add_argument(
        "--running",
        type=bool,
        help="Take control of the already running chrome instance in debug mode with LinkedIn signed in",
        default=False,
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port number of the already running chrome instance in debug mode with LinkedIn signed in",
        default=9222,
    )
    parser.add_argument(
        "--save",
        type=bool,
        help="Save the output in a json file",
        default=False,
    )
    parser.add_argument(
        "--debug",
        type=bool,
        help="Debug mode",
        default=False,
    )

    args = parser.parse_args()

    ### ARGUMENTS PARSED ###

    ### LOGGING CONFIG ###
    logging.basicConfig(filename="app.log", filemode="w")

    # adding sep log file for selenium
    selenium_logger = logging.getLogger("selenium.webdriver")
    selenium_logger.setLevel(logging.CRITICAL)

    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    ### GETTING DRIVERS ###

    if not args.running:
        config = ConfigParser()
        try:
            config.read("config.ini")
        except Exception as e:
            logging.exception(e)
            logging.critical("Error in reading config file")

        username = config["linkedin"]["username"]
        password = config["linkedin"]["password"]

        url = "https://www.linkedin.com/"
        driver = get_selenium_drivers(args.running, headless=args.headless)
        sign_in(url, driver, username, password)
    else:
        driver = get_selenium_drivers(args.running, portnumber=args.port)

    ### DRIVER ACQUIRED ###

    if args.path is not None:
        profile_urls = parse_urls_from_filepath(path=args.path)
        for url in profile_urls:
            extract_profile_information(url, driver, args.save)
    else:
        extract_profile_information(args.url, driver, args.save)

    exit(0)        
