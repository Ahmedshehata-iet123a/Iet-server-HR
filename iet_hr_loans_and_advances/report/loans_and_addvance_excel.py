# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api,_
from num2words import num2words


class departmentReportExcel(models.AbstractModel):
    _name = 'report.iet_hr_loans_and_advances.loans_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, loans):
        # style
        sheet = workbook.add_worksheet('Loans Report')
        heading = workbook.add_format({"font_size": 16,'num_format': 'yyyy-mm-dd','left': True,'valign': 'center', 'bold': True, 'bg_color': '#fffbed', })
        date_style = workbook.add_format({'num_format': 'yyyy-mm-dd','left': True,'valign': 'left', 'bold': True, 'bg_color': '#fffbed', 'align': 'center', })
        center_style = workbook.add_format({'valign': 'center', 'bold': True, 'bg_color': '#fffbed', })
        title_center_style = workbook.add_format({'valign': 'center', 'bold': True, 'bg_color': '#f2eee4', })
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#FFFF00', 'border': True})
        title = workbook.add_format(
            {'bold': True, 'align': 'center', 'font_size': 17, 'bg_color': '#eae5db', 'border': True})
        sub_title = workbook.add_format(
            {'bold': True, 'align': 'center', 'font_size': 13, 'bg_color': '#eae5db', 'border': True})
        for l in loans:
            row = 6
            col = 0
            sheet.set_column(0, 0, 10)
            sheet.set_column(1, 1, 40)
            sheet.set_column(2, 2, 40)
            sheet.set_column(3, 3, 40)
            sheet.set_column(4, 4, 40)
            sheet.set_row(row, 20)
            sheet.merge_range('A1:F2', 'Loans Report ( %s ) ' % l.name, title)
            row += 2
            sheet.merge_range('B4:C5', 'Employee( %s ) ' % l.employee_id.name, heading)
            row += 2
            sheet.merge_range('B7:C8', 'Department( %s ) ' % l.department_id.name, heading)
            row += 2
            sheet.merge_range('B9:C10', 'Amount( %s ) ' % l.amount, heading)
            row += 2
            sheet.merge_range('B11:C12', 'Employee Number( %s ) ' % l.barcode_for_loan, heading)
            row += 2
            list_data = []
            num = 0
            for r in loans.loans_ids:
                num += 1
                list_data.append(
                    {
                        'num': num,
                        'name': r.name,
                        'delay': r.delay,
                        'amount': r.amount,
                        'is_paid': r.is_paid,
                    }
                )
            sheet.set_row(row, 40)
            sheet.write(row, 0, '#', heading)
            sheet.write(row, 1, 'Date', heading)
            sheet.write(row, 2, 'Delay', heading)
            sheet.write(row, 3, 'amount', heading)
            sheet.write(row, 4, 'Is Paid', heading)
            # print('list_data==', list_data)
            for l in list_data:
                sheet.set_row(row, 40)
                row += 2
                # sheet.merge_range(row, col, row, col + 5, pr['--'], title)
                sheet.write(row, 0, l['num'], center_style)
                sheet.write(row, 1, l['name'], date_style)
                sheet.write(row, 2, l['delay'], center_style)
                sheet.write(row, 3, l['amount'], center_style)
                sheet.write(row, 4, l['is_paid'], center_style)
                sheet.set_row(row, 40)
            row += 2
