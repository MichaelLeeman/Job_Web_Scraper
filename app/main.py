# This program scraps data from job postings on the website workinstartups.com and appends it to an excel worksheet.

import os
from datetime import datetime, timedelta
from selenium import webdriver
from app import web_scraper
from app import excel

URL = "https://workinstartups.com/job-board/jobs-in/london"
soup = web_scraper.soup_creator(URL, max_retry=1, sleep_time=0)

job_list, last_date = [], None

driver = webdriver.Chrome('./chromedriver')
driver.get(URL)
driver.find_element_by_link_text('Close').click()

file_path = os.path.abspath("main.py").rstrip('/app/main.py') + '//Workbooks' + "//Job_Openings.xlsx"

# If the Job_Openings workbook already exists then append the jobs not already in the worksheet
# by checking the date of the first job in excel, since the last time the site was scraped.
if os.path.isfile(file_path):
    workbook, worksheet = excel.load_xlsx(file_path)
    last_scrape_date = excel.get_first_job_date(worksheet)
    last_scrape_date = datetime.strptime(last_date, "%d-%b-%Y")
# If not, create a new workbook and append all of the jobs posted within the month
else:
    current_date = datetime.today()
    date_month_ago = current_date - timedelta(weeks=4.348)  # Average amount of weeks in a month
    last_scrape_date = date_month_ago.replace(hour=0, minute=0, second=0, microsecond=0)  # default to midnight
    workbook, worksheet = excel.init_xlsx(worksheet_title="Job Openings")

# Scrap the jobs from workinstartups.com and update the worksheet with the found jobs
job_list = web_scraper.search_for_jobs(soup, last_scrape_date, driver)
driver.close()
excel.update_xlsx(worksheet, job_list)
excel.save_xlsx(workbook, file_path)
