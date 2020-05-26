# This program scraps data from job postings on the website workinstartups.com and appends it to an excel worksheet.
# So far, the program scraps job titles and company names using BeautifulSoup and adds the data to excel using
# openpyxl.

import requests
from openpyxl import Workbook
from openpyxl.styles import Font
from bs4 import BeautifulSoup

# -----------------------------------------------------------------------
# Web Scraping
# -----------------------------------------------------------------------

URL = "https://workinstartups.com/job-board/jobs-in/london"
page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")


# Extracts the job title from each job posting
def extract_job_title_from_result(soup):
    jobs = []
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):
        for a in div.find_all(name="a"):  # Job titles are the only elements with "a" tags in the posting.
            jobs.append(a["title"])
    return jobs


# Extracts the company name from each job posting
def extract_company_name_from_result(soup):
    companies = []
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):  # For each job posting
        for span in div.find_all(name="span", attrs={"style": "display: ruby-base-container"}):
            text_in_span = span.string
            formatted_text = text_in_span.strip().replace('\n', ' ').replace('\t', '').replace('at ', '').replace(
                ' in London', '')   # Removes unwanted info in string. May need to improve this.
            companies.append(formatted_text)
    return companies


extracted_jobs = extract_job_title_from_result(soup)
extracted_companies = extract_company_name_from_result(soup)

# -----------------------------------------------------------------------
# Excel
# -----------------------------------------------------------------------

file_path = "Job_Openings.xlsx"
book = Workbook()
sheet1 = book.active

sheet1["A1"] = "Job Openings"
sheet1["B1"] = "Company"
sheet1["A1"].font = Font(bold=True)  # May need to change this in future titles as it's repetitive
sheet1["B1"].font = Font(bold=True)


# Adds each job title after the less entry in the "Job Openings" column.
def add_jobs_to_xl(job_list):
    for job in job_list:
        job_row = sheet1.max_row + 1
        job_cell_coord = 'A' + str(job_row)
        sheet1[job_cell_coord] = job


# Adds each company name after the less entry in the "Company" column.
def add_company_to_xl(company_list):
    # This chunk finds the row where column B ends at.
    first_blank_row = 2
    for row in range(2, sheet1.max_row):
        if sheet1['B' + str(row)].value is not None:
            first_blank_row += 1

    # Adds each of the company names to the cells just after the less entry in the "Company" column.
    i = 0
    new_last_row = first_blank_row + len(company_list)
    for row in range(first_blank_row, new_last_row):
        sheet1.cell(row=row, column=2, value=company_list[i])
        i += 1


add_jobs_to_xl(extracted_jobs)
add_company_to_xl(extracted_companies)
book.save(file_path)
