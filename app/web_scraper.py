# This module makes requests to workinstartups.com and scrapes data from each job posting.

import time as t
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


# Makes a GET request to the URL and retries the connection if a connection error occurs.
def get_request(URL_link, max_retry=3):
    current_page, request_worked, number_of_total_retries = None, False, 0
    while number_of_total_retries < max_retry and not request_worked:
        try:
            current_page = requests.get(URL_link, headers={"User-Agent": "Chrome/83.0"}, allow_redirects=False)
            request_worked = True
            return current_page
        except requests.exceptions.ConnectionError as err:
            print("Connection error to " + str(URL_link) + " has failed.")
            print("Retrying the connection to the URL attempt number: " + str(number_of_total_retries+1))
            t.sleep((2 ** number_of_total_retries)-1)   # Sleep times [ 0.0s, 1.0s, 3.0s]
            number_of_total_retries += 1
            if number_of_total_retries >= max_retry:
                raise err


# Creates a soup from the URL and waits for the  elements to load.
def soup_creator(URL_link, max_retry=3, sleep_time=0.5):
    current_page = get_request(URL_link, max_retry)
    current_soup = BeautifulSoup(current_page.text, "html.parser")
    t.sleep(sleep_time)
    return current_soup


# Extracts details from the current job posting
def scrape_job_post(div):
    job_hyperlink = div.a["href"]
    job_title = div.a["title"]
    company_name = div.find(name="span", attrs={"style": "display: ruby-base-container"}).string.split(None, 2)[1]
    job_type = div.find("span").string

    # Format the date posted to match other dates
    unformatted_date = div.find("span", attrs={"style": "order: 2"}).string.strip()
    date_posted = datetime.strptime(unformatted_date, "%d-%m-%Y").strftime('%d-%b-%Y')

    # Scrapes for extra details found inside the job's description page (deadline, salary range, etc.).
    job_description_soup = soup_creator(job_hyperlink)

    # Deadline is written in a string text. To extract the date, the text is converted to a list.
    date_text_into_list = job_description_soup.find("small").string.split()[8: 11]
    separator = '-'
    expiry_date = separator.join(date_text_into_list)  # Joining only the day, month and year back into a string

    # Sometimes the salary range might be given in the salary icon, others specified in the text. If not then assign "Unspecified salary".
    salary_contents = job_description_soup.find(attrs={"class": "mb-3 mb-sm-0"})

    if salary_contents is not None:
        # If salary is given in the icon then the salary range can be scraped from it like a list
        salary_range = salary_contents.contents[1].strip()
    else:
        # Unpaid positions, commission only and other salary types are only specified in the job description text
        salary_range, commission_already_added, equity_already_added = "Unspecified salary", False, False

        for p_element in job_description_soup.find_all(name="p"):
            job_description_text = p_element.text.lower()

            unpaid_terms = ["unpaid", "voluntary", "volunteer", "no salary"]
            if any(unpaid_term in job_description_text for unpaid_term in unpaid_terms):
                salary_range = "Unpaid"

            elif "competitive salary" in job_description_text:
                salary_range = "Competitive salary"

            # sometimes the salary is given in the job description's text. These are found by searching for common characters.
            elif "£" in job_description_text:
                salary_range = ""
                # Find a word in the text that seems to resemble a salary range
                for word in job_description_text.split():
                    word = word.strip('-').strip(",").strip(".")
                    if word.startswith("£"):
                        salary_range += word
                        # Formatting to remove unwanted characters or add wanted characters at the end
                        if word.endswith("0"):
                            salary_range += " - "
                        # Rarely words containing "£" are not salaries but something like the market shares in millions/billions.
                        elif "m" in word or "b" in word:
                            salary_range = "Unspecified salary"
                    # Sometimes the upper range is separated from the lower range making it a new word. So add it.
                    elif word.endswith("000"):
                        salary_range += word

                # Formatting by removing unwanted characters on the end of the string
                salary_range = salary_range.strip(" - ")
                # Adding spaces between the salary range
                if "0-£" in salary_range:
                    index = salary_range.find("0-£")
                    salary_range = salary_range[:index] + "0 - £" + salary_range[index+3:]
                # Adding "per year" at the end of salaries in thousands
                if salary_range.endswith("000") or salary_range.endswith("k"):
                    salary_range += " per year"

            # Some jobs have commission with other salary types. Others have only commission.
            if "commission" in job_description_text:
                if not commission_already_added:
                    salary_range += " + commission"
                    commission_already_added = True
                commission_terms = ["commission only", "commission-only", "only commission", "commission based"]
                if any(commission_term in job_description_text for commission_term in commission_terms):
                    salary_range = "Unpaid"
                    break

            # Some jobs only provide equity, others have it on top of a salary.
            if "equity" in job_description_text:
                if not equity_already_added:
                    salary_range += " + equity"
                    equity_already_added = True
                equity_terms = ["equity only", "equity-only", "only equity", "equity based"]
                if any(equity_term in job_description_text for equity_term in equity_terms):
                    salary_range = "Equity only"
                    break

    # Scraping the hyperlink to the company's website
    company_hyperlink_element = job_description_soup.find(attrs={"class": "d-flex my-4 container"})
    company_hyperlink = company_hyperlink_element.a["href"]

    # Sometimes company URLs aren't given which means the next found element with attribute href is a link to another page
    if "https://workinstartups.com/" in company_hyperlink:
        company_hyperlink = None

    job_details = (job_title, company_name, job_type, date_posted, expiry_date, salary_range)
    return job_details, job_hyperlink, company_hyperlink


# Scrape the job postings on the current page while the date is not later than last_date
def scrape_page(soup, last_date, job_list, hyperlink_list, company_link_list):
    keep_searching = True
    for div in soup.find_all(name="div", attrs={"class": "job-listing mb-2"}):
        job_details, job_hyperlink, company_hyperlink = scrape_job_post(div)
        job_date = datetime.strptime(job_details[3], '%d-%b-%Y')
        # Stops the search if the jobs' postings have a later date than last_date
        if job_date < last_date:
            keep_searching = False
            break
        # Append the job if it's in date
        hyperlink_list.append(job_hyperlink)
        company_link_list.append(company_hyperlink)
        job_list.append(job_details)
    return job_list, hyperlink_list, company_link_list, keep_searching


# Goes to the next page
def go_to_new_page(driver):
    driver.find_element_by_link_text('Next >').click()
    new_soup = soup_creator(driver.current_url)
    return new_soup


# Keeps scraping for jobs on the current page while checking that they aren't older than a fortnight ago.
def search_for_jobs(current_soup, last_date_to_check, driver):
    job_list, hyperlink_list, company_link_list = [], [], []
    keep_searching = True
    while keep_searching:
        job_list, hyperlink_list, company_link_list, keep_searching = scrape_page(current_soup, last_date_to_check, job_list, hyperlink_list, company_link_list)
        current_soup = go_to_new_page(driver)
    return job_list, hyperlink_list, company_link_list
