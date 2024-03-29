# Job_Web_Scraper
This project is a Python web-scraper and Excel program that extracts data from job websites and presents the data in an Excel worksheet.

![](/images/worksheet_screenshot.png)
## Table Of Contents
* [About](#about)
* [Technologies](#technologies)
* [How To Setup](#how-to-setup)
* [Sources](#sources)

## About
The purpose of this project is learn how to scrape data and create Excel worksheets using Python. 

So far, this program scrapes data from the job website workinstartups.com by extracting keywords such as dates and salary range from the job description texts. The program then cleans the data and organises it by date.

Finally, the program creates a new Excel worksheet called _Job_Openings.xlsx_ in the project's directory (on the first time running). This Excel worksheet contains a table presenting all of the scraped job openings. If the program is ran again later on, then new jobs will be added to _Job_Openings.xlsx_, and any jobs that are past their deadline will be removed.


## Technologies
Project was created with:
* Python: 3.8
* requests: 2.23.0
* beautifulsoup4: 4.9.0
* selenium: 3.141.0
* openpyxl: 3.0.3

## How To Setup
To setup the project, you need to clone the repo using Git, create a virtual environment and install dependencies from requirements.txt. You can do this from the terminal:

```buildoutcfg
# Clone project repository and enter project directory
$ git clone https://github.com/MichaelLeeman/Job_Web_Scraper
$ cd Job_Web_Scraper

# Creating virtualenv and activate it
$ python3 -m venv my_venv
$ source ./my_venv/bin/activate

# Install dependencies
$ pip3 install -r ./requirements.txt
```
Next, you need to install [Chrome driver](https://sites.google.com/a/chromium.org/chromedriver/downloads) to allow Selenium to interface with Google Chrome. This application is built for Google Driver version 85.0 but other versions could be used by changing the header parameters in GET requests. The chrome driver needs to be installed in the app's directory.

Finally, you can run the program inside the app directory. Please note that the program takes approximately 15 minutes to run with stable internet connection. While the app is running, an automated Google Chrome browser that's controlled by Selenium should pop up. Afterwards, you can open the Excel workbook by entering the following in the terminal:
```buildoutcfg
# Run Python program
$ python3 main.py
```
Finally, the workbook should be located in the Workbooks directory with the name _Job_Openings.xlsx_.

## Sources

This project was inspired by [Web Scraping Job Postings from Indeed](https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b) article  by Michael Salmon. 

The [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [Selenium with Python](https://selenium-python.readthedocs.io/) and [OpenPyXl Documentation](https://openpyxl.readthedocs.io/en/stable/) were also used for this project.
