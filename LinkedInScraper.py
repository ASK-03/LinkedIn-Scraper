import re
import os
from bs4 import BeautifulSoup as bs
import time
import logging
import json
from typing import List, Dict
import jsonschema



class LinkedinScraper:
    def __init__(self, profile: str, driver: object, save: bool) -> None:
        self.profile = bs(profile, "lxml")
        self.driver = driver
        self.save = save
        self.url = self.driver.current_url
        self.metadata = self.get_metadata()
        self.name = self.get_name()
        self.location = self.get_location()
        self.experience = (
            self.get_experience()
            if self.metadata["sectionExists"]["experience"]
            else [self.get_dict("experience")]
        )
        self.education = (
            self.get_education()
            if self.metadata["sectionExists"]["education"]
            else [self.get_dict("education")]
        )
        self.volunteering = (
            self.get_volunteering()
            if self.metadata["sectionExists"]["volunteering_experience"]
            else [self.get_dict("volunteering")]
        )
        self.skills = (
            self.get_skills()
            if self.metadata["sectionExists"]["skills"]
            else [self.get_dict("skills")]
        )
        self.output = self.get_json_output()


    def get_name(self) -> str or None:
        try:
            name = (
                self.profile.find("div", attrs={"class": "pv-text-details__left-panel"})
                .find("div")
                .find("h1")
                .text
            )
        except Exception as e:
            logging.exception(e)
            logging.error("div element for name not found...")
            name = None

        return name

    def get_location(self) -> str or None:
        try:
            location = self.profile.find(
                "span",
                attrs={"class": "text-body-small inline t-black--light break-words"},
            ).text
        except Exception as e:
            logging.exception(e)
            logging.error("span element for location not found...")
            location = None
        return location

    def get_metadata(self) -> dict:
        temp = self.profile.find_all("span", attrs={"class": "pvs-navigation__text"})

        s = "".join(i.text for i in temp)

        store = {
            0: "experience",
            1: "education",
            2: "volunteering_experience",
            3: "skills",
        }
        metadata = {
            "sectionExists": {
                "experience": False,
                "education": False,
                "volunteering_experience": False,
                "skills": False,
            },
            "showAllButtonExists": {
                "experience": False,
                "education": False,
                "volunteering_experience": False,
                "skills": False,
            },
        }
        patterns = [
            r"Show all \d+ experiences",
            r"Show all \d+ education",
            r"Show all \d+ volunteer experiences",
            r"Show all \d+ skills",
        ]
        for idx, pattern in enumerate(patterns):
            if re.search(pattern, s):
                metadata["showAllButtonExists"][store[idx]] = True

        for section in store.values():
            temp = self.profile.find("div", attrs={"id": f"{section}"})

            if temp is None:
                continue
            else:
                metadata["sectionExists"][section] = True

        return metadata

    def get_experience(self) -> List:
        experience_list = []
        if self.metadata["showAllButtonExists"]["experience"]:
            self.driver.get(self.url + "details/experience/")
            time.sleep(2)

            experience = self.driver.page_source
            experience = bs(experience, "lxml")

            experience = self.get_lists(experience)

            logging.debug("experience page loaded...")
        else:
            experience = self.profile.find("div", attrs={"id": "experience"}).parent
            experience = experience.find("ul").find_all(
                "li",
                attrs={
                    "class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"
                },
            )
            logging.debug("using profile page...")

        for exp in experience:
            experience_dict = self.get_dict("experience")

            temp = exp.find(
                "div", attrs={"class": "display-flex flex-row justify-space-between"}
            ).find_all("span", attrs={"class": "visually-hidden"})

            ### TITLE ###
            experience_dict["title"] = temp[0].text

            ### COMPANY ###
            company = temp[1].text
            company = company.replace(" ", "").split("·")
            if len(company) == 2:
                experience_dict["company"] = company[0]
                experience_dict["employmentType"] = company[1]

            if len(company) == 1:
                if company[0] in [
                    "Full-time",
                    "Part-time",
                    "Self-employed",
                    "Freelance",
                    "Internship",
                    "Trainee",
                ]:
                    experience_dict["employmentType"] = company[0]
                else:
                    experience_dict["company"] = company[0]

            ### DURATION ###
            if len(temp) > 2:
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
                if len(location) == 2:
                    experience_dict["location"] = location[0]
                    experience_dict["locationType"] = location[1]

                ### taken care of the case where one of the locationType or location is not present
                if len(location) == 1:
                    if location[0] in ["Remote", "On-site", "Hybrid"]:
                        experience_dict["locationType"] = location[0]
                    else:
                        experience_dict["location"] = location[0]

            experience_list.append(experience_dict)

        return experience_list

    def get_education(self) -> List:
        education_list = []

        if self.metadata["showAllButtonExists"]["education"]:
            self.driver.get(self.url + "details/education/")
            time.sleep(2)

            education = self.driver.page_source
            education = bs(education, "lxml")

            education = self.get_lists(education)
            logging.debug("education page loaded...")

        else:
            education = self.profile.find("div", attrs={"id": "education"}).parent
            education = education.find("ul").find_all(
                "li",
                attrs={
                    "class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"
                },
            )
            logging.debug("using profile page...")

        for edu in education:
            education_dict = self.get_dict("education")

            temp = edu.find(
                "div", attrs={"class": "display-flex flex-row justify-space-between"}
            ).find_all("span", attrs={"class": "visually-hidden"})

            ### SCHOOL ###
            education_dict["school"] = temp[0].text

            if len(temp) == 3:
                ### DEGREE ###
                temp1 = temp[1].text
                temp1 = temp1.split(",")
                if len(temp1) == 1:
                    education_dict["degree"] = temp1[0]
                else:
                    education_dict["degree"] = temp1[0]
                    education_dict["fieldOfStudy"] = temp1[1]

                ### DURATION ###
                duration = temp[2].text
                duration = duration.split("-")
                education_dict["startDate"] = duration[0]
                education_dict["endDate"] = duration[1]
                try:
                    education_dict["duration"] = abs(
                        int(duration[0].replace(" ", ""))
                        - int(duration[1].replace(" ", ""))
                    )
                except Exception as e:
                    logging.error(e)
                    logging.error("start date and end date not in required format")

            elif len(temp) == 2:
                # Now we have to check if the first element is degree or duration
                pattern = re.compile(r"\d{4}\s-\s\d{4}")
                match = re.findall(pattern, temp[1].text)
                if len(match) == 0:
                    # this means that the first element is degree
                    temp1 = temp[1].text
                    temp1 = temp1.split(",")
                    if len(temp1) == 1:
                        education_dict["degree"] = temp1[0]
                    else:
                        education_dict["degree"] = temp1[0]
                        education_dict["fieldOfStudy"] = temp1[1]
                else:
                    # this means that the first element is duration
                    duration = temp[1].text
                    duration = duration.split("-")
                    education_dict["startDate"] = duration[0]
                    education_dict["endDate"] = duration[1]
                    try:
                        education_dict["duration"] = abs(
                            int(duration[0].replace(" ", ""))
                            - int(duration[1].replace(" ", ""))
                        )
                    except Exception as e:
                        logging.error(e)
                        logging.error("start date and end date not in required format")
                # education_dict["duration"] = duration[1]
            education_list.append(education_dict)

        return education_list

    def get_volunteering(self) -> List:
        volunteer_list = []
        if self.metadata["showAllButtonExists"]["volunteering_experience"]:
            self.driver.get(self.url + "details/volunteering-experiences/")
            time.sleep(2)

            volunteer = self.driver.page_source
            volunteer = bs(volunteer, "lxml")
            volunteer = self.get_lists(volunteer)
            logging.debug("volunteer page loaded...")
        else:
            volunteer = self.profile.find("div", attrs={"id": "volunteer"}).parent
            volunteer = volunteer.find("ul").find_all(
                "li",
                attrs={
                    "class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"
                },
            )
            logging.debug("using profile page...")

        for vol in volunteer:
            volunteer_dict = self.get_dict("volunteering")

            temp = vol.find(
                "div", attrs={"class": "display-flex flex-row justify-space-between"}
            ).find_all("span", attrs={"class": "visually-hidden"})

            volunteer_dict["role"] = temp[0].text

            volunteer_dict["organisation"] = temp[1].text

            if len(temp) == 2:
                pattern = re.compile(r"\d{4}\s-\s\d{4}")
                match = re.findall(pattern, temp[1].text)
                if len(match) != 0:
                    ### DURATION ###
                    duration = temp[2].text
                    duration = duration.replace(" ", "").split("·")
                    start_end = duration[0].split("-")
                    volunteer_dict["startDate"] = start_end[0]
                    volunteer_dict["endDate"] = start_end[1]
                    volunteer_dict["duration"] = duration[1]
                else:
                    volunteer_dict["cause"] = temp[2].text
            elif len(temp) == 3:
                ### DURATION ###
                duration = temp[2].text
                duration = duration.replace(" ", "").split("·")
                start_end = duration[0].split("-")
                volunteer_dict["startDate"] = start_end[0]
                volunteer_dict["endDate"] = start_end[1]
                volunteer_dict["duration"] = duration[1]

                volunteer_dict["cause"] = temp[3].text

            volunteer_list.append(volunteer_dict)

        return volunteer_list

    # TODO: not all the skills are visible in one go, so we need to click on the show more button or scroll down sometimes.
    def get_skills(self) -> List:
        skills_list = []

        if self.metadata["showAllButtonExists"]["skills"]:
            self.driver.get(self.url + "details/skills/")
            time.sleep(2)

            skills = self.driver.page_source
            skills = bs(skills, "lxml")

            skills = self.get_lists(skills)
            logging.debug("skills page loaded...")
        else:
            skills = self.profile.find("div", attrs={"id": "skills"}).parent
            skills = skills.find("ul").find_all(
                "li",
                attrs={
                    "class": "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"
                },
            )
            logging.debug("using profile page...")

        for skill in skills:
            skill_dict = self.get_dict("skills")

            temp = (
                skill.find(
                    "div",
                    attrs={"class": "display-flex flex-row justify-space-between"},
                )
                .find("span", attrs={"class": "visually-hidden"})
                .text
            )

            skill_dict["skill"] = temp

            skills_list.append(skill_dict)

        return skills_list

    def get_dict(self, type: str) -> Dict:
        temp = {}
        if type == "experience":
            temp = {
                "title": None,
                "company": None,
                "employmentType": None,
                "startDate": None,
                "endDate": None,
                "duration": None,
                "location": None,
                "locationType": None,
            }
        elif type == "education":
            temp = {
                "school": None,
                "degree": None,
                "fieldOfStudy": None,
                "startDate": None,
                "endDate": None,
                "duration": None,
            }
        elif type == "volunteering":
            temp = {
                "role": None,
                "organisation": None,
                "startDate": None,
                "endDate": None,
                "duration": None,
                "cause": None,
            }
        elif type == "skills":
            temp = {
                "skill": None,
            }
        else:
            logging.critical("Invalid type")

        return temp

    def get_lists(self, source: object) -> List:
        try:
            return (
                source.find("main", attrs={"class": "scaffold-layout__main"})
                .find("section", attrs={"class": "artdeco-card ember-view pb3"})
                .find("div", attrs={"class": "pvs-list__container"})
                .find("ul")
                .find_all(
                    "li",
                    attrs={
                        "class": "pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"
                    },
                )
            )
        except Exception as e:
            logging.exception(e)
            logging.critical(
                "li elements not found... try again or check the class names"
            )
            return None

    def get_json_output(self) -> str:
        output = json.dumps(
            {
                "url": self.url,
                "name": self.name,
                "location": self.location,
                "experience": self.experience,
                "education": self.education,
                "volunteering": self.volunteering,
                "skills": self.skills,
            },
            indent=4,
        )

        return output

    def save_output_in_file(self) -> None:
        if self.save:
            filename = self.url.split("/")[-2]
            try:
                import json

                if not os.path.exists("./data"):
                    os.makedirs("data")
                with open(f"./data/{filename}.json", "w", encoding="utf-8") as f:
                    f.write(self.output)
                    logging.critical(f"File saved as {filename}.json")
            except Exception as e:
                logging.exception(e)
                logging.critical("Error in saving the file")
        else:
            return None