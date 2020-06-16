# This program scraps data from job postings on the website workinstartups.com and appends it to an excel worksheet.
# So far, the program scraps job titles and company names using BeautifulSoup and adds the data to excel using
# openpyxl.

import time as t
from selenium import webdriver
import requests
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# -----------------------------------------------------------------------
# Web Scraping
# -----------------------------------------------------------------------

URL = "https://workinstartups.com/job-board/jobs-in/london"
page = requests.get(URL, headers={"User-Agent": "Chrome/83.0"})
soup = BeautifulSoup(page.text, "html.parser")

driver = webdriver.Chrome('./chromedriver')
driver.get("https://workinstartups.com/job-board/jobs-in/london")
driver.find_element_by_link_text('Close').click()

job_list, hyperlink_list = [], []
current_date = datetime.today()
date_fortnight_ago = current_date - timedelta(weeks=2)
last_recent_date = date_fortnight_ago.replace(hour=0, minute=0, second=0, microsecond=0)    # default to midnight


# Extracts the job details and hyperlink from each job posting on the current page
def scrape_job_details(soup):
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):
        job_hyperlink = div.a["href"]
        job_title = div.a["title"]
        company_name = div.find(name="span", attrs={"style": "display: ruby-base-container"}).string.split(None, 2)[1]
        job_type = div.find("span").string

        # Format the date posted to match other dates
        unformatted_date = div.find("span", attrs={"style": "order: 2"}).string.strip()
        date_posted = datetime.strptime(unformatted_date, "%d-%m-%Y").strftime('%d-%b-%Y')

        expiry_date, salary_range = more_job_details(job_hyperlink)

        hyperlink_list.append(job_hyperlink)
        job_list.append((job_title, company_name, job_type, date_posted, expiry_date, salary_range))
    return job_list, hyperlink_list


# Scrapes for extra job details found inside the job's description web page.
def more_job_details(job_hyperlink):
    try:
        current_page = requests.get(job_hyperlink, headers={"User-Agent": "Chrome/83.0"}, allow_redirects=False)
        current_page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    new_soup = BeautifulSoup(current_page.text, "html.parser")
    t.sleep(0.5)

    # Deadline is written in a string text. To extract the date, the text is converted to a list.
    date_text_into_list = new_soup.find("small").string.split()[8: 11]
    separator = '-'
    expiry_date = separator.join(date_text_into_list)   # Joining only the day, month and year back into a string

    # Salary range is scraped from a list. If there is no job salary then assign "Not specified"
    salary_contents = new_soup.find(attrs={"class": "mb-3 mb-sm-0"})

    if salary_contents is not None:
        salary_range = salary_contents.contents[1].strip()
    else:
        salary_range = "Not specified"
        # Unpaid and voluntary positions are only specified in the job description text
        for job_description_element in new_soup.find_all(name="p"):
            job_description_text = job_description_element.text.lower()
            if "unpaid" in job_description_text:
                salary_range = "Unpaid"
            elif "voluntary" in job_description_text:
                salary_range = "Unpaid"
            elif "volunteer" in job_description_text:
                salary_range = "Unpaid"
    return expiry_date, salary_range


# Checks the date posted of every job and removes it if it's too old
# Returns a boolean to stop searching for jobs on the next pages
def remove_outdated_jobs(job_list, keep_searching):
    for job in job_list[:]:
        job_datetime = datetime.strptime(job[3], '%d-%b-%Y')    # Needs to convert back to datetime to make comparison
        if job_datetime < last_recent_date:
            job_list.remove(job)
            keep_searching = False
    return job_list, keep_searching


# Goes to the next page
def go_to_new_page():
    driver.find_element_by_link_text('Next >').click()

    try:
        current_page = requests.get(driver.current_url, headers={"User-Agent": "Chrome/83.0"})
        current_page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    new_soup = BeautifulSoup(current_page.text, "html.parser")
    return new_soup


# Keep adding the jobs from the page until they are older than than "last_recent_date"
def search_for_jobs(current_soup):
    keep_searching_for_jobs = True
    while keep_searching_for_jobs:
        unsorted_job_list, URL_list = scrape_job_details(current_soup)
        sorted_job_list, keep_searching_for_jobs = remove_outdated_jobs(unsorted_job_list, keep_searching_for_jobs)
        t.sleep(0.5)
        current_soup = go_to_new_page()
        t.sleep(0.5)
    return sorted_job_list, URL_list


job_list, hyperlink_list = search_for_jobs(soup)
driver.close()


# -----------------------------------------------------------------------
# Excel
# -----------------------------------------------------------------------


def setup_worksheet(worksheet):
    title_names = ("Job Openings", "Company", "Job Type", "Date Posted", "Deadline", "Salary Range")
    worksheet.append(title_names)

    # Stylise the titles
    for column_title in worksheet[1:1]:
        column_title.font = Font(bold=True, color='FFFFFF')
        column_title.fill = PatternFill(start_color="2196F3", fill_type="solid")

    append_job_to_xl(job_list, worksheet)

    # Autofits the columns by taking the length of the longest entry
    for column_cell in worksheet.columns:
        max_char_len = 0
        for cell in column_cell:
            if max_char_len < len(str(cell.value)):     # Datetime types need to become strings to measure len
                max_char_len = len(str(cell.value))
        new_column_length = max_char_len
        worksheet.column_dimensions[column_cell[0].column_letter].width = new_column_length

    # Colours every other row light blue
    for every_other_row in range(3, worksheet.max_row + 1, 2):
        for cell in worksheet[every_other_row]:
            cell.fill = PatternFill(start_color="BBDEFB", fill_type="solid")


# Appends each job opening to the worksheet and creates a hyperlink to its page
def append_job_to_xl(job_list, worksheet):
    URL_index = 0
    for job in job_list:
        worksheet.append(job)
        current_row = worksheet._current_row
        # Adds a hyperlink to each job web page in the job title column
        worksheet["A" + str(current_row)].hyperlink = hyperlink_list[URL_index]
        URL_index += 1


file_path = "Job_Openings.xlsx"
book = Workbook()
sheet1 = book.active
setup_worksheet(sheet1)
book.save(file_path)
