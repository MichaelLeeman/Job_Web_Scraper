# This module setups the excel worksheet, stylise it and appends the job data

from openpyxl.styles import Font, PatternFill
from openpyxl import Workbook


# setups the worksheet by appending the data and calling the other styling functions
def setup_worksheet(worksheet, job_list, hyperlink_list, company_link_list, table_headers):
    worksheet.append(table_headers)
    create_table_headers(worksheet, font_colour="FFFFFF", cell_colour="2196F3")
    append_job_to_xl(job_list, hyperlink_list, company_link_list, worksheet)
    autofit_columns(worksheet)
    colour_rows(worksheet, colour="BBDEFB")
    filter_and_freeze_panes(worksheet)


# Stylise the titles
def create_table_headers(worksheet, font_colour, cell_colour):
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
def append_job_to_xl(job_list, hyperlink_list, company_link_list, worksheet):
    URL_index = 0
    for job in job_list:
        worksheet.append(job)
        current_row = worksheet._current_row
        # Adds a hyperlink to each job web page in the job title column
        worksheet["A" + str(current_row)].hyperlink = hyperlink_list[URL_index]
        if company_link_list[URL_index] is not None:
            worksheet["B" + str(current_row)].hyperlink = company_link_list[URL_index]
        URL_index += 1


# Initialise the workbook and worksheet
def init_workbook(worksheet_title):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = worksheet_title
    return workbook, worksheet


# Saves the workbook
def save_workbook(workbook, file_path):
    workbook.save(file_path)
