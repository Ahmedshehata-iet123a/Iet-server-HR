# from odoo import api, fields, models
#
#
# class PosProductsReportExcel(models.AbstractModel):
#     _name = 'report.iet_hr_employee_enhancement.employee_report_excel'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, objs):
#         sheet = workbook.add_worksheet('Employees Report Excell')
#         main_title = workbook.add_format(
#             {'font_size': 16,
#              'border': True, 'align': 'center', 'valign': 'vcenter',
#              'bold': True, 'bg_color': '#008080', 'font_color': 'white'})
#         space_title = workbook.add_format(
#             {'align': 'center', 'valign': 'vcenter',
#              'bold': True, 'bg_color': 'white', 'font_color': 'white'})
#         header_format = workbook.add_format(
#             {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'valign': 'vcenter',
#              'top': True, 'align': 'center', 'bg_color': '#008080', 'font_color': 'white',
#              'bold': True})
#         line_format = workbook.add_format(
#             {'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'valign': 'vcenter',
#              'top': True, 'align': 'center', 'bg_color': 'white', 'font_color': 'black',
#              'bold': True})
#
#         config = self.env['ir.config_parameter'].sudo()
#         insurance_info_config = config.get_param('iet_hr_employee_enhancement.hr_employee_insurance_information', )
#
#         start_row, end_row, start_col, end_col = 0, 3, 0, 11
#         for row in range(start_row, end_row + 1):
#             for col in range(start_col, end_col):
#                 if col != end_col:
#                     sheet.merge_range(row, col, row, end_col, "", space_title)
#         row = end_row + 1
#
#         for col in range(0, 8):
#             sheet.set_column(col, col, 10) if col == 0 else sheet.set_column(col, col,
#                                                                              30) if col == 1 else sheet.set_column(col,
#                                                                                                                    col,
#                                                                                                                    30) if col == 2 else sheet.set_column(
#                 col,
#                 col,
#                 30) if col == 7 else sheet.set_column(
#                 col,
#                 col,
#                 20)
#         for col in range(8, 18):
#             sheet.set_column(col, col, 40)
#         sheet.set_row(row, 25)
#         if insurance_info_config:
#             sheet.merge_range(row, 0, row, 17, "Employee Report Excel", main_title)
#         else:
#             sheet.merge_range(row, 0, row, 13, "Employee Report Excel", main_title)
#         row += 1
#         sheet.set_row(row, 50)
#         sheet.write(row, 0, "Count", header_format)
#         sheet.write(row, 1, "Employee Name", header_format)
#         sheet.write(row, 2, "Employee Number", header_format)
#         sheet.write(row, 3, "Department", header_format)
#         sheet.write(row, 4, "Contract", header_format)
#         sheet.write(row, 5, "Contract Start", header_format)
#         sheet.write(row, 6, "Contract End", header_format)
#         sheet.write(row, 7, "Contract Change Days", header_format)
#         sheet.write(row, 8, "Identification Number", header_format)
#         sheet.write(row, 9, "Identification End", header_format)
#         sheet.write(row, 10, "Identification Change Days", header_format)
#         sheet.write(row, 11, "Passport Number", header_format)
#         sheet.write(row, 12, "Passport Expiration Date", header_format)
#         sheet.write(row, 13, "Passport Expiration days", header_format)
#         if insurance_info_config:
#             sheet.write(row, 14, "Insurance Policy Number", header_format)
#             sheet.write(row, 15, "Medical Insurance Scheme", header_format)
#             sheet.write(row, 16, "Insurance Termination Date", header_format)
#             sheet.write(row, 17, "Insurance Termination Days", header_format)
#
#
#         row += 1
#         employee_domain = [('contract_id.state', '=', "open"), ('contract_id.state', '=', "open")]
#         employee_ids = self.env['hr.employee'].search(employee_domain, order="id asc")
#         print("@@@@@@@@@@@@@@@@@@@@", employee_ids)
#         counter = 0
#         for employee in employee_ids:
#             contract = employee.contract_id
#             counter += 1
#             sheet.write(row, 0, counter, line_format)
#             sheet.write(row, 1, employee.name, line_format)
#             sheet.write(row, 2, employee.custom_employee_pin_number,
#                         line_format)
#             sheet.write(row, 3, employee.department_id.name, line_format)
#             sheet.write(row, 4, contract.name, line_format)
#             sheet.write(row, 5, str(contract.date_start), line_format)
#             sheet.write(row, 6, str(contract.date_end), line_format)
#             today = fields.Date.today()
#             change_days = str((contract.date_end - today).days) if contract.date_end else False
#             sheet.write(row, 7, change_days, line_format)
#             sheet.write(row, 8, employee.identification_id, line_format)
#             sheet.write(row, 9, str(employee.end_date_identification), line_format)
#             identification_days = str(
#                 (employee.end_date_identification - today).days) if employee.end_date_identification else 0
#             sheet.write(row, 10, identification_days, line_format)
#             sheet.write(row, 11, employee.passport_id, line_format)
#             sheet.write(row, 12, str(employee.end_date_passport), line_format)
#             expiration_days = str(
#                 (employee.end_date_passport - today).days) if employee.end_date_passport else 0
#             sheet.write(row, 13, expiration_days, line_format)
#             if insurance_info_config:
#                 sheet.write(row, 14, employee.insurance_policy_number, line_format)
#                 sheet.write(row, 15, employee.insurance_medical, line_format)
#                 sheet.write(row, 16, str(employee.insurance_end_date), line_format)
#                 insurance_change_days = str((employee.insurance_end_date - today).days) \
#                     if employee.insurance_end_date else False
#                 sheet.write(row, 17, insurance_change_days, line_format)
#             row += 1
#
#
#
from odoo import api, fields, models


class PosProductsReportExcel(models.AbstractModel):
    _name = 'report.iet_hr_employee_enhancement.employee_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Employees Report Excel')

        main_title = workbook.add_format({
            'font_size': 16,
            'border': True, 'align': 'center', 'valign': 'vcenter',
            'bold': True, 'bg_color': '#008080', 'font_color': 'white'
        })
        space_title = workbook.add_format({
            'align': 'center', 'valign': 'vcenter',
            'bold': True, 'bg_color': 'white', 'font_color': 'white'
        })
        header_format = workbook.add_format({
            'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'valign': 'vcenter',
            'top': True, 'align': 'center', 'bg_color': '#008080', 'font_color': 'white',
            'bold': True
        })
        line_format = workbook.add_format({
            'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'valign': 'vcenter',
            'top': True, 'align': 'center', 'bg_color': 'white', 'font_color': 'black',
            'bold': True
        })

        config = self.env['ir.config_parameter'].sudo()
        insurance_info_config = config.get_param('iet_hr_employee_enhancement.hr_employee_insurance_information')

        start_row, end_row, start_col, end_col = 0, 3, 0, 11

        # Adjust merge range logic to avoid overlap
        if end_col > start_col:
            sheet.merge_range(start_row, start_col, end_row, end_col, "", space_title)

        row = end_row + 1

        # Set column widths
        for col in range(0, 8):
            width = 30 if col != 0 else 10
            sheet.set_column(col, col, width)
        for col in range(8, 18):
            sheet.set_column(col, col, 40)

        sheet.set_row(row, 25)
        merge_end_col = 17 if insurance_info_config else 13
        sheet.merge_range(row, 0, row, merge_end_col, "Employee Report Excel", main_title)

        row += 1
        sheet.set_row(row, 50)

        # Write headers
        headers = [
            "Count", "Employee Name", "Employee Number", "Department", "Contract",
            "Contract Start", "Contract End", "Contract Change Days",
            "Identification Number", "Identification End", "Identification Change Days",
            "Passport Number", "Passport Expiration Date", "Passport Expiration days"
        ]

        if insurance_info_config:
            headers += [
                "Insurance Policy Number", "Medical Insurance Scheme",
                "Insurance Termination Date", "Insurance Termination Days"
            ]

        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_format)

        row += 1
        employee_domain = [('contract_id.state', '=', "open")]
        employee_ids = self.env['hr.employee'].search(employee_domain, order="id asc")
        counter = 0

        for employee in employee_ids:
            contract = employee.contract_id
            counter += 1
            sheet.write(row, 0, counter, line_format)
            sheet.write(row, 1, employee.name, line_format)
            sheet.write(row, 2, employee.custom_employee_pin_number, line_format)
            sheet.write(row, 3, employee.department_id.name, line_format)
            sheet.write(row, 4, contract.name, line_format)
            sheet.write(row, 5, str(contract.date_start), line_format)
            sheet.write(row, 6, str(contract.date_end), line_format)
            today = fields.Date.today()
            change_days = str((contract.date_end - today).days) if contract.date_end else 0
            sheet.write(row, 7, change_days, line_format)
            sheet.write(row, 8, employee.identification_id, line_format)
            sheet.write(row, 9, str(employee.end_date_identification), line_format)
            identification_days = str(
                (employee.end_date_identification - today).days) if employee.end_date_identification else 0
            sheet.write(row, 10, identification_days, line_format)
            sheet.write(row, 11, employee.passport_id, line_format)
            sheet.write(row, 12, str(employee.end_date_passport), line_format)
            expiration_days = str((employee.end_date_passport - today).days) if employee.end_date_passport else 0
            sheet.write(row, 13, expiration_days, line_format)

            if insurance_info_config:
                sheet.write(row, 14, employee.insurance_policy_number, line_format)
                sheet.write(row, 15, employee.insurance_medical, line_format)
                sheet.write(row, 16, str(employee.insurance_end_date), line_format)
                insurance_change_days = str(
                    (employee.insurance_end_date - today).days) if employee.insurance_end_date else 0
                sheet.write(row, 17, insurance_change_days, line_format)

            row += 1