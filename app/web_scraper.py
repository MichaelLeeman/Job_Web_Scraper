# This module makes requests to workinstartups.com and scrapes data from each job posting.

import time as t
import requests
from bs4 import BeautifulSoup
from datetime import datetime


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
            print("Retrying the connection to the URL attempt number: " + str(number_of_total_retries + 1))
            t.sleep((2 ** number_of_total_retries) - 1)  # Sleep times [ 0.0s, 1.0s, 3.0s]
            number_of_total_retries += 1
            if number_of_total_retries >= max_retry:
                raise err


# Creates a soup from the URL and waits for the  elements to load.
def soup_creator(URL_link, max_retry=3, sleep_time=0.5):
    current_page = get_request(URL_link, max_retry)
    current_soup = BeautifulSoup(current_page.text, "html.parser")
    t.sleep(sleep_time)
    return current_soup


# Finds the salary range in the text of the job description.
def salary_finder(job_description_soup, tag_to_search):
    salary_range = "Unspecified salary"

    for p_element in job_description_soup.find_all(name=tag_to_search):
        job_description_text = p_element.text.lower()

        # Unpaid positions, commission only and other salary types are only specified in the job description text
        if any(unpaid_term in job_description_text for unpaid_term in
               ("unpaid", "voluntary", "volunteer", "no salary")):
            salary_range = "Unpaid"

        elif "competitive" in job_description_text or "appropriate salary" in job_description_text:
            salary_range = "Competitive salary"

        # sometimes the salary is given in the job description's text. These are found by searching for common characters.
        elif "£" in job_description_text:
            if any(other_term in salary_range for other_term in ("Unpaid", "Commission only", "Equity only")):
                break
            else:
                # Find a word in the text that seems to resemble a salary range
                text_list, salary_index = job_description_text.lower().split(), 0
                for word in text_list:
                    current_word_index = text_list.index(word)
                    word = word.strip('-').strip(",").strip(".")
                    if word.startswith("£"):
                        # Rarely words containing "£" are not salaries but something like the market shares in millions/billions.
                        if any(unwanted_term in word for unwanted_term in ("b", "m", "s", "££")):
                            salary_range = "Unspecified salary"
                        else:
                            # Check ahead of the string for words that are not associated with salaries
                            salary_index = current_word_index
                            try:
                                if any(amount in text_list[salary_index + 1] for amount in
                                       ("million", "billion")):
                                    salary_range = "Unspecified salary"
                                    break
                            except IndexError:
                                pass
                            # Reformat salaries written in "k" format into "000" format and add it to salary range
                            word = word.replace("k", ",000")
                            salary_range = salary_range.replace("Unspecified salary", "").replace("Competitive salary", "")
                            salary_range += word + " - "
                    # Sometimes the upper range is separated from the lower range making it a new word. So add it.
                    elif "000" in word:
                        salary_index = current_word_index
                        salary_range += word

                # Formatting by removing unwanted characters from the string and changing thousand separator to comma
                salary_range = salary_range.strip(" - ").replace(".000", ",000")
                salary_range = salary_range.replace("/annual", " per year").replace("/month", " per month")

                # Adding spaces between the salary range
                if "0-" in salary_range:
                    index = salary_range.find("0-")
                    salary_range = salary_range[:index] + "0 - " + salary_range[index + 2:]

                # Adding "per year" at the end of salaries in thousands
                if salary_range.endswith("000"):
                    salary_range += " per year"
                else:
                    # Check ahead of the string whether the salary is paid per hour, per day or etc.
                    try:
                        if "hour" in text_list[salary_index + 1]:
                            salary_range += " per hour"
                        elif "day" in text_list[salary_index + 1]:
                            salary_range += " per day"
                        elif "week" in text_list[salary_index + 1]:
                            salary_range += " per week"
                        elif "month" in text_list[salary_index + 1]:
                            salary_range += " per month"
                        elif "hour" in text_list[salary_index + 2]:
                            salary_range += " per hour"
                        elif "day" in text_list[salary_index + 2]:
                            salary_range += " per day"
                        elif "week" in text_list[salary_index + 2]:
                            salary_range += " per week"
                        elif "month" in text_list[salary_index + 2]:
                            salary_range += " per month"
                    except IndexError:
                        pass
    salary_range = salary_additions(job_description_text, salary_range)
    return salary_range


# Find whether the job offers salary add-ons such as commission or equity. Also, find whether the job is commission or equity only.
def salary_additions(job_description_text, salary_range):
    # Some jobs have commission with other salary types. Others have only commission.
    if "commission" in job_description_text:
        if "commission" not in salary_range:
            salary_range += " + commission"
        if any(commission_term in job_description_text for commission_term in
               ("commission only", "commission-only", "only commission", "commission based")):
            salary_range = "Commission only"

    # Some jobs only provide equity, others have it on top of a salary.
    if "equity" in job_description_text:
        if "equity" not in salary_range:
            salary_range += " + equity"
        if any(equity_term in job_description_text for equity_term in
               ("equity only", "equity-only", "only equity", "equity based")):
            salary_range = "Equity only"

    # Find if the job offers bonuses
    if "bonus" in job_description_text:
        # If bonus is not already in salary_range
        if "bonus" not in salary_range:
            # Jobs sometimes uses the word bonus to describe additional non-required skills/experiences
            if any(non_bonus_term in job_description_text for non_bonus_term in
                   ("experience", "points", "skill")):
                pass
            else:
                # Find the index of the bonus in the string
                text_list = job_description_text.lower().split()
                for word in text_list:
                    if "bonus" in word:
                        bonus_index = text_list.index(word)
                try:
                    # Look at the previous words before the bonus word. Again, jobs describe additional skills/experiences
                    # with sentences like "it would be a bonus to have..." or "It is a bonus to have.."
                    previous_words = " ".join(text_list[bonus_index - 3: bonus_index])
                    if "would be a" in previous_words:
                        pass
                    elif "is a" in previous_words:
                        pass
                    else:
                        salary_range += " + bonus"
                except (ValueError, UnboundLocalError):
                    pass

    # Reposition the salary add-ons in salary_range string to the correct order
    for salary_add_on in ("+ commission", "+ equity", "+ bonus"):
        if salary_range.startswith(salary_add_on):
            salary_range = salary_range[len(salary_add_on):] + " " + salary_range[:len(salary_add_on)]
    return salary_range


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
        # Find the salary add-ons in the job description page
        for tag in ("p", "li"):
            for p_element in job_description_soup.find_all(name=tag):
                job_description_text = p_element.text.lower()
                salary_range = salary_additions(job_description_text, salary_range.lower())
    else:
        # Else, find whether the salary in given in the text tags of the job description page
        salary_range = salary_finder(job_description_soup, tag_to_search="p")
        if salary_range == "Unspecified salary":
            salary_range = salary_finder(job_description_soup, tag_to_search="li")
        elif salary_range == "Competitive salary":
            found_salary = salary_finder(job_description_soup, tag_to_search="li")
            if found_salary.startswith("£") or "per" in found_salary:
                salary_range = found_salary

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
        job_list, hyperlink_list, company_link_list, keep_searching = scrape_page(current_soup, last_date_to_check,
                                                                                  job_list, hyperlink_list,
                                                                                  company_link_list)
        current_soup = go_to_new_page(driver)
    return job_list, hyperlink_list, company_link_list
