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


def setup_worksheet(worksheet):
    title_names = ("Job Openings", "Company")
    worksheet.append(title_names)

    for column_title in worksheet[1:1]:
        column_title.font = Font(bold=True, color='FFFFFF')
        column_title.fill = PatternFill(start_color="2196F3", fill_type="solid")

    add_jobs_to_xl(extracted_jobs, worksheet)
    add_company_to_xl(extracted_companies, worksheet)

    # Autofits the columns by taking the length of the longest entry
    for column_cell in worksheet.columns:
        max_char_len = 0
        for cell in column_cell:
            if max_char_len < len(cell.value):
                max_char_len = len(cell.value)
        new_column_length = max_char_len * 0.87
        worksheet.column_dimensions[column_cell[0].column_letter].width = new_column_length

    # Colour every other row blue
    for every_other_row in range(3, worksheet.max_row + 1, 2):
        for cell in worksheet[every_other_row]:
            cell.fill = PatternFill(start_color="BBDEFB", fill_type="solid")

# Adds each job title after the less entry in the "Job Openings" column.
def add_jobs_to_xl(job_list, worksheet):
    for job in job_list:
        job_row = worksheet.max_row + 1
        job_cell_coord = 'A' + str(job_row)
        worksheet[job_cell_coord] = job


# Adds each company name after the less entry in the "Company" column.
def add_company_to_xl(company_list, worksheet):
    # Finds the row where column B ends.
    first_blank_row = 2
    for row in range(2, worksheet.max_row):
        if worksheet['B' + str(row)].value:
            first_blank_row += 1

    # Adds each of the company names to the cells after the last entry of the column.
    i = 0
    new_last_row = first_blank_row + len(company_list)
    for row in range(first_blank_row, new_last_row):
        worksheet.cell(row=row, column=2, value=company_list[i])
        i += 1


file_path = "Job_Openings.xlsx"
book = Workbook()
sheet1 = book.active
setup_worksheet(sheet1)
book.save(file_path)
