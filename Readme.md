
# LinkedIn Profile Scraper

The LinkedIn Profile Scraper is a tool designed to extract information from the profile page of a given URL on LinkedIn. It provides an automated way to gather data from LinkedIn profiles, such as personal details, work experience, education, skills, and more.

## Features

Automatically extracts the information like, name, location, experience, education, skills of the profile page of the given URL and returns the output in JSON format.

## Dependencies
- **Python3**: Ensure that you have Python 3 installed on your system. You can download and install Python 3 from the official Python website: https://www.python.org.
- **pip**: pip is the package installer for Python. It is usually installed by default when you install Python. However, make sure you have pip installed and it is up to date. You can check the version of pip by running the following command:
  ```
  pip --version
  ```
- **Selenium**: You can install it using pip by running the following command
  ```
  pip install selenium
  ```
- **Chromium Drivers**: Make sure you have the appropriate Chromium drivers installed and configured. These drivers are required for Selenium to interact with the Chromium browser. Refer to the Selenium documentation for instructions on installing and setting up Chromium drivers based on your operating system.


## Installation

To install and use carrer-scraper, follow the steps given below:
- Fork the carrer-scraper repository by clicking the "Fork" button at the top right corner of the repository page. This will create a copy of the repository under your GitHub account.
- Clone the forked repository to your local machine:
  ```
  git clone https://github.com/{YOUR-USERNAME}/career-scraper   
  ```
- Navigate to the project directory: 
  ```
  cd carrer-scraper
  ```
- Install the necessary Python packages by running the following command:
  ```
  pip install -r requirements.txt
  ```
- Navigate to the ``scraper.py``
  ```
  cd profile-scraper
  ```

## How to use?

To use LinkedIn Scraper, follow the steps given below:

**(Recommended)**

- Login to the LinkedIn account from the account you want to do scraping using Google Chrome and keep it signed in.
- **For ubuntu**, open the terminal and use the given command to start Google chrome in remote debugging mode
    ```
    google-chrome --remote-debugging-port=PORT_NUMBER --user-data-dir="~/.config/google-chrome
    ```
    Replace the ``PORT_NUMBER`` with a port number, you would like your chrome browser to run on.

- Now, you can run the scraper.py using the following command:
    ```
    python3 scraper.py --running True --portnumber PORT_NUMBER
    ```
    Replace ``PORT_NUMBER`` by the port number on which the google chrome is running

    This will use the signed in account to extract the data from the LinkedIn profiles

**Note:** This method has lower risks of failure.

**(Other)**
- Open config.ini file in a text editor, and add you preferable LinkedIn account's login credentials.
- Run the scraper.py using the following command:
    ```
    python3 scraper.py
    ```

## Contributions

Contributions to carrer-scraper are welcome! If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request on the GitHub repository.

## Author

- [Abhishek Singh Kushwaha](https://github.com/ASK-03)

## Mentor

- [Kumar Shivendu](https://github.com/KShivendu)