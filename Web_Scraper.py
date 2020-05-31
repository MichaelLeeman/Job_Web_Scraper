# This program scraps data from job postings on the website workinstartups.com and appends it to an excel worksheet.
# So far, the program scraps job titles and company names using BeautifulSoup and adds the data to excel using
# openpyxl.

import requests
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from bs4 import BeautifulSoup

# -----------------------------------------------------------------------
# Web Scraping
# -----------------------------------------------------------------------

URL = "https://workinstartups.com/job-board/jobs-in/london"
page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")


# Extracts the job details from each job posting
def extract_job_details(soup):
    job_info = []
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):
        for a in div.find_all(name="a"):  # Job titles are the only elements with "a" tags in the posting.
            job_title = a["title"]
        for span in div.find_all(name="span", attrs={"style": "display: ruby-base-container"}):
            text_in_span = span.string
            company_name = text_in_span.strip().replace('\n', ' ').replace('\t', '').replace('at ', '').replace(
                ' in London', '')   # Removes unwanted info in string. May need to improve this.
        for span in div.find_all(name="span", attrs={"class": "job-listing-category badge badge-pill badge-light"}):
            job_type = span.string
        for span in div.find_all(name="span", attrs={"style": "order: 2"}):
            unformatted_date = span.string
            date_posted = unformatted_date.strip()
        job_info.append((job_title, company_name, job_type, date_posted))
    return job_info


extracted_jobs = extract_job_details(soup)

# -----------------------------------------------------------------------
# Excel
# -----------------------------------------------------------------------


def setup_worksheet(worksheet):
    title_names = ("Job Openings", "Company", "Job Type", "Date Posted")
    worksheet.append(title_names)

    # Stylise the titles
    for column_title in worksheet[1:1]:
        column_title.font = Font(bold=True, color='FFFFFF')
        column_title.fill = PatternFill(start_color="2196F3", fill_type="solid")

    append_job_to_xl(extracted_jobs, worksheet)

    # Autofits the columns by taking the length of the longest entry
    for column_cell in worksheet.columns:
        max_char_len = 0
        for cell in column_cell:
            if max_char_len < len(cell.value):
                max_char_len = len(cell.value)
        new_column_length = max_char_len * 0.95
        worksheet.column_dimensions[column_cell[0].column_letter].width = new_column_length

    # Colours every other row blue
    for every_other_row in range(3, worksheet.max_row + 1, 2):
        for cell in worksheet[every_other_row]:
            cell.fill = PatternFill(start_color="BBDEFB", fill_type="solid")


# Appends each job opening to the worksheet.
def append_job_to_xl(job_list, worksheet):
    for job in job_list:
        worksheet.append(job)


file_path = "Job_Openings.xlsx"
book = Workbook()
sheet1 = book.active
setup_worksheet(sheet1)
book.save(file_path)
