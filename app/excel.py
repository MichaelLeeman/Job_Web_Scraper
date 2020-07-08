# This module setups the excel worksheet, stylise it and appends the job data

from openpyxl.styles import Font, PatternFill
from openpyxl import Workbook
from openpyxl import load_workbook


# setups the worksheet by appending the data and calling the other styling functions
def setup_xlsx(worksheet, job_list, hyperlink_list, company_link_list):
    append_jobs_to_xl(job_list, hyperlink_list, company_link_list, worksheet)
    autofit_columns(worksheet)
    colour_rows(worksheet, colour="BBDEFB")
    filter_and_freeze_panes(worksheet)


# Stylise the titles
def create_table_headers(worksheet, font_colour, cell_colour):
    table_headers = ("Job Openings", "Company", "Job Type", "Date Posted", "Deadline", "Salary Range")
    worksheet.append(table_headers)

    for column_title in worksheet[1:1]:
        column_title.font = Font(bold=True, color=font_colour)
        column_title.fill = PatternFill(start_color=cell_colour, fill_type="solid")


# Autofits the columns by taking the length of the longest entry
def autofit_columns(worksheet):
    for column_cell in worksheet.columns:
        max_char_len = 0
        for cell in column_cell:
            if max_char_len < len(str(cell.value)):  # Datetime types need to become strings to measure len
                max_char_len = len(str(cell.value)) * 1.35
        new_column_length = max_char_len
        worksheet.column_dimensions[column_cell[0].column_letter].width = new_column_length


# Colours every other row with the colour parameter
def colour_rows(worksheet, colour):
    for every_other_row in range(2, worksheet.max_row + 1):
        for cell in worksheet[every_other_row]:
            cell.fill = PatternFill(start_color="FFFFFF", fill_type="solid")

    for every_other_row in range(3, worksheet.max_row + 1, 2):
        for cell in worksheet[every_other_row]:
            cell.fill = PatternFill(start_color=colour, fill_type="solid")


# Add filter and freeze pane
def filter_and_freeze_panes(worksheet):
    worksheet.auto_filter.ref = worksheet.dimensions
    freeze_above = worksheet['A2']
    worksheet.freeze_panes = freeze_above
    return worksheet


# Appends each job opening to the worksheet and creates a hyperlink to its page
def append_jobs_to_xl(job_list, hyperlink_list, company_link_list, worksheet):
    URL_index, first_xl_job = 0, tuple(cell.value for row in worksheet["A2":"B2"] for cell in row)

    # Fixes bug where a blank row is appended
    if worksheet["A2"].value is None:
        worksheet.delete_rows(2)

    # Only append jobs that are not already in the worksheet.
    for job in job_list:
        # Rather than compare each job in the worksheet, only compare it to the first job to save time
        if job[:2] != first_xl_job:
            worksheet.append(job)
            current_row = worksheet._current_row

            # Adds a hyperlink to each job web page in the job title column
            worksheet["A" + str(current_row)].hyperlink = hyperlink_list[URL_index]

            # If the company link was given then add the hyperlink
            if company_link_list[URL_index] is not None:
                worksheet["B" + str(current_row)].hyperlink = company_link_list[URL_index]
            URL_index += 1
        # Stop adding jobs from job_list to the worksheet
        else:
            break


# Initialise a new workbook and worksheet
def init_xlsx(worksheet_title):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = worksheet_title
    create_table_headers(worksheet, font_colour="FFFFFF", cell_colour="2196F3")
    return workbook, worksheet


# Loads an existing workbook
def load_xlsx(file_path):
    workbook = load_workbook(filename=file_path)
    worksheet = workbook.active
    return workbook, worksheet


# Saves the workbook
def save_xlsx(workbook, file_path):
    workbook.save(file_path)
