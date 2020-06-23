from openpyxl.styles import Font, PatternFill

# -----------------------------------------------------------------------
# Excel
# -----------------------------------------------------------------------


def setup_worksheet(worksheet, job_list, hyperlink_list, company_link_list):
    title_names = ("Job Openings", "Company", "Job Type", "Date Posted", "Deadline", "Salary Range")
    worksheet.append(title_names)

    # Stylise the titles
    for column_title in worksheet[1:1]:
        column_title.font = Font(bold=True, color='FFFFFF')
        column_title.fill = PatternFill(start_color="2196F3", fill_type="solid")

    append_job_to_xl(job_list, hyperlink_list, company_link_list, worksheet)

    # Autofits the columns by taking the length of the longest entry
    for column_cell in worksheet.columns:
        max_char_len = 0
        for cell in column_cell:
            if max_char_len < len(str(cell.value)):  # Datetime types need to become strings to measure len
                max_char_len = len(str(cell.value))
        new_column_length = max_char_len
        worksheet.column_dimensions[column_cell[0].column_letter].width = new_column_length

    # Colours every other row light blue
    for every_other_row in range(3, worksheet.max_row + 1, 2):
        for cell in worksheet[every_other_row]:
            cell.fill = PatternFill(start_color="BBDEFB", fill_type="solid")

    # Add filter and freeze pane
    worksheet.auto_filter.ref = worksheet.dimensions
    freeze_above = worksheet['A2']
    worksheet.freeze_panes = freeze_above


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


