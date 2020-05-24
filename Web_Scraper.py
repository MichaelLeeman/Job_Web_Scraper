import requests
from openpyxl import Workbook
from openpyxl.styles import Font
from bs4 import BeautifulSoup

URL = "https://workinstartups.com/job-board/jobs-in/london"
page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")


# print(soup.prettify())


# Extracts the job title from each job posting
def extract_job_title_from_result(soup):
    jobs = []
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):  # For each job posting
        for a in div.find_all(
                name="a"):  # For each job title. The job titles are the only elements with "a" tags in the job posting.
            jobs.append(a["title"])
    return jobs


def extract_company_name_from_result(soup):
    companies = []  # Maybe use sets to remove duplicates
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):  # For each job posting
        for span in div.find_all(name="span", attrs={
            "style": "display: ruby-base-container"}):  # For each job title. The job titles are the only elements with "a" tags in the job posting.
            text_in_span = span.string
            formatted_text = text_in_span.strip().replace('\n', ' ').replace('\t', '').replace('at ', '').replace(
                ' in London', '')
            companies.append(formatted_text)
    return companies


extracted_jobs = extract_job_title_from_result(soup)
extracted_companies = extract_company_name_from_result(soup)

# Excel part of the code:

file_path = "Example.xlsx"
book = Workbook()
sheet1 = book.active

sheet1["A1"] = "Job Openings"
sheet1["A1"].font = Font(bold=True)  # May need to change this for other titles
# ws1 = wb.create_sheet("Job Openings")
sheet1["B1"] = "Company"
sheet1["B1"].font = Font(bold=True)


def add_jobs_to_xl(job_list):
    for job in job_list:
        job_row = sheet1.max_row + 1
        job_cell_coord = 'A' + str(job_row)
        sheet1[job_cell_coord] = job


def add_company_to_xl(company_list):
    first_blank_row = 2        # This chunk is to find what row column B ends at.
    for row in range(2, sheet1.max_row):
        if sheet1['B' + str(row)].value is not None:
            first_blank_row += 1

    i = 0
    new_last_row = first_blank_row + len(company_list)
    for row in range(2, new_last_row):
        sheet1.cell(row=row, column=2, value=company_list[i])
        i += 1


add_jobs_to_xl(extracted_jobs)
add_company_to_xl(extracted_companies)
book.save(file_path)
