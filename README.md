# Job_Web_Scraper
A simple Python web-scraper and Excel program that extracts data from job websites and presents the data in an Excel Worksheet.

## Table Of Contents
* [About](#about)
* [Technologies](#technologies)
* [How To Setup](#how-to-setup)
* [Sources](#sources)

## About
The purpose of this project to learn how to web-scrape and write Excel worksheets using Python. 

So far, this program web-scrapes from the job website workinstartups.com and extracts data from recent job openings from multiple pages. The program then creates a new Excel worksheet in the project's directory, showing all of the recent job openings in a table.  

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
Next, you need to install the [Chrome driver](https://sites.google.com/a/chromium.org/chromedriver/downloads) to allow Selenium to interface with Google Chrome. The chrome driver needs to be installed in the app's directory.

Finally, you can run the program inside the app directory and open the Excel workbook by entering the following in the terminal:
```buildoutcfg
# Run Python program
$ python3 web_scraper.py

# open Excel workbook
$ open Job_Openings.xlsx
```
The workbook should be located in the app directory with the name _Job_Openings.xlsx_.

## Sources

This project was inspired by [Web Scraping Job Postings from Indeed](https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b) article  by Michael Salmon, where snippets of code were modified. 

The [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [Selenium with Python](https://selenium-python.readthedocs.io/) and [OpenPyXl Documentation](https://openpyxl.readthedocs.io/en/stable/) were also used for this project.
