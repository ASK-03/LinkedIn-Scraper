"""
Code by : Abhishek Singh Kushwaha
"""

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from configparser import ConfigParser
import argparse


def quit_driver(self, driver):
        print("quitting driver...")
        driver.quit()


def get_selenium_drivers(running: bool, **kwargs) -> object:
    options = Options()
    options.add_argument("--window-size=1920,1080")
    if running:
        portnumber = kwargs.get("portnumber", 9222)
        options.add_experimental_option("debuggerAddress", f"localhost:{portnumber}")
    else:
        options.add_experimental_option("detach", True)

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    time.sleep(2)
    print("waiting for the drivers to start...")
    return driver


def sign_in(url, driver, username, password):
    print("Starting to load the page...")
    driver.get(url)
    time.sleep(3)
    print("Page loaded...")

    print("signing in...")

    username_input_box = driver.find_element(By.ID, value="session_key")
    username_input_box.send_keys(username)
    time.sleep(0.5)

    password_input_box = driver.find_element(By.ID, value="session_password")
    password_input_box.send_keys(password)
    time.sleep(0.5)

    btn = driver.find_element(
        By.CLASS_NAME, value="sign-in-form__submit-btn--full-width"
    )
    btn.click()
    time.sleep(10)

    print("signed in...")


def get_profile(driver, url):
    if driver.current_url != url:
        print("getting profile...")

        driver.get(url)
        time.sleep(3)

        print("profile loaded...")
    else:
        print("profile already loaded...")

    profile = driver.page_source
    return profile


class Extract_information_from_profile:
    def __init__(self, profile, driver) -> None:
        self.profile = bs(profile, "lxml")
        self.driver = driver
        self.name = self.get_name()
        self.location = self.get_location()
        self.experience = self.get_experience()
        self.education = self.get_education()
        self.skills = self.get_skills()

    def get_name(self):
        name = (
            self.profile.find("div", attrs={"class": "pv-text-details__left-panel"})
            .find("div")
            .find("h1")
            .text
        )
        return name

    def get_location(self):
        location = self.profile.find(
            "span", attrs={"class": "text-body-small inline t-black--light break-words"}
        ).text
        return location

    def get_experience(self):
        experience_list = []

        self.driver.get(self.driver.current_url + "details/experience/")
        time.sleep(5)

        experience = self.driver.page_source
        experience = bs(experience, "lxml")

        experience = (
            experience.find("main", attrs={"class": "scaffold-layout__main"})
            .find("section", attrs={"class": "artdeco-card ember-view pb3"})
            .find("div", attrs={"class": "pvs-list__container"})
            .find("ul")
            .find_all("li", attrs={"class": "pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"})
        )
        # print(len(experience))
        # print(experience)

        for exp in experience:

            experience_dict = {
                "title": None,
                "company": None,
                "employmentType": None,
                "startDate": None,
                "endDate": None,
                "duration": None,
                "location": None,
                "locationType": None,
            }

            temp = (
                exp.find("div", attrs={"class": "display-flex flex-row justify-space-between"})
                .find_all("span", attrs={"class": "visually-hidden"})
            )

            ### TITLE ###
            experience_dict["title"] = temp[0].text

            ### COMPANY ###
            company = temp[1].text
            company = company.replace(" ", "").split("·")
            if len(company) == 2:
                experience_dict["company"] = company[0]
                experience_dict["employmentType"] = company[1]
            
            if len(company) == 1:
                if company[0] in ["Full-time", "Part-time", "Self-employed", "Freelance", "Internship", "Trainee"]:
                    experience_dict["employmentType"] = company[0]
                else:
                    experience_dict["company"] = company[0]
            
            ### DURATION ###
            duration = temp[2].text
            duration = duration.replace(" ", "").split("·")
            start_end = duration[0].split("-")
            experience_dict["startDate"] = start_end[0]
            experience_dict["endDate"] = start_end[1]
            experience_dict["duration"] = duration[1]

            ### LOCATION ###
            location = temp[3].text
            location = location.replace(" ", "").split("·")
            
            # if both locationType and location are present
            if len(location)==2:
                experience_dict["location"] = location[0]
                experience_dict["locationType"] = location[1]
            
            ### taken care of the case where one of the locationType or location is not present
            if len(location)==1: 
                if location[0] in ["Remote", "On-site", "Hybrid"]:
                    experience_dict["locationType"] = location[0]
                else:
                    experience_dict["location"] = location[0]   

            experience_list.append(experience_dict)

        return experience_list
    
    #### FUNCTIONS TO COMPLETE ####

    def get_education(self):
        pass

    def get_skills(self):
        pass

    ### FUNCTION TO COMPLETE ###

    def get_output_in_json(self, object):
        from json import dumps

        print("converting to json...")
        if type == str:
            return dumps(object, indent=4)
        if type == "array":
            for i in range(len(object)):
                object[i] = dumps(object[i], indent=4)
        print("converted to json...")
        return dumps(object, indent=4)


if __name__ == "__main__":
    ### PARSING ARGUMENTS ##
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--running",
        type=bool,
        help="Take control of the already running chrome instance in debug mode with LinkedIn signed in",
        default=False,
    )
    parser.add_argument(
        "--portnumber",
        type=int,
        help="Port number of the already running chrome instance in debug mode with LinkedIn signed in",
        default=9222,
    )

    args = parser.parse_args()

    ### ARGUMENTS PARSED ###

    ### GETTING DRIVERS ###

    if not args.running:
        config = ConfigParser()
        config.read("config.ini")

        username = config["linkedin"]["username"]
        password = config["linkedin"]["password"]

        url = "https://www.linkedin.com/"
        driver = get_selenium_drivers(args.running)
        sign_in(url, driver, username, password)
    else:
        driver = get_selenium_drivers(args.running, portnumber=args.portnumber)

    ### DRIVER ACQUIRED ###

    ### GETTING PROFILE ###
    profile_url = "https://www.linkedin.com/in/kshivendu/"
    page_source = get_profile(driver, profile_url)
    ### PROFILE ACQUIRED ###

    ### EXTRACTING INFORMATION ###
    time.sleep(5)
    extractor = Extract_information_from_profile(page_source, driver)

    print(extractor.name)
    print(extractor.location)
    print(extractor.experience)
    ### INFORMATION EXTRACTED ###

