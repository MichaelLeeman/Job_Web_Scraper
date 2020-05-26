# Job_Web_Scraper
A simple Python web-scraper and Excel program that extracts data from job websites and presents the data in an Excel Worksheet.

## Table Of Contents
* [About](#About)
* [Technologies](#technologies)
* [How To Setup](#how to setup)
* [To Do List](#to do list)
* [Sources](#sources)

## About
The purpose of this project is for me to learn how to web-scrape with Python. So far, this program web-scrapes from the job website workinstartups.com. It extracts data from job openings on the first page, including job titles and company names. The program then creates a new Excel worksheet in the project's directory, showing all of the job openings in a table.  

## Technologies
Project was created with:
* Python: 3.8
* requests: 2.23.0
* beautifulsoup4: 4.9.0
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

# Run Python program and open Excel workbook
$ python3 Web_Scraper.py
$ open Job_Openings.xlsx
```
Once you have done this, an Excel workbook should open up called "Job_Openings.xlsx". This Excel workbook can be located in the project's directory.

## To Do List
* Format the worksheet's table including resizing the columns, colouring the cells and adding a title to the table.
* Scrape through more than one page of workinstartups.com.
* Implement a better function for appending data to the end of the columns.
* Extract more data including: 
    * Type of job (full-time, part-time, freelance, etc.) 
    * Date posted
    * Salary
* Web scrape other job boards:
    * Angel
    * Company website's career page

## Sources

This project was inspired by [Web Scraping Job Postings from Indeed](https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b) article  by Michael Salmon, where snippets of code were modified. 

The [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and [OpenPyXl Documentation](https://openpyxl.readthedocs.io/en/stable/) were also used for this project.
