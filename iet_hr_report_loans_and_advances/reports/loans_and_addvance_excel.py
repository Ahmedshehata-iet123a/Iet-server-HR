# -*- coding: utf-8 -*-
from odoo import models



class DepartmentReportExcel(models.AbstractModel):
    _name = 'report.iet_hr_report_loans_and_advances.loans_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        header_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'border': 1
        })

        cell_style = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'border': 1
        })

        number_style = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'border': 1,
            'num_format': '#,##0.00'
        })

        title_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
            'border': 1
        })

        sheet = workbook.add_worksheet("Loans & Salary Advances")

        columns_widths = [20, 40, 20, 20, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        for idx, width in enumerate(columns_widths):
            sheet.set_column(idx, idx, width)

        sheet.merge_range('A1:M1', 'Loans & Salary Advance & Housing Advance Report', title_style)
        sheet.set_row(0, 30)
        sheet.set_row(1, 20)

        sheet.write_blank('A2', None, header_style)
        sheet.write_blank('B2', None, header_style)
        sheet.write_blank('C2', None, header_style)
        sheet.write_blank('D2', None, header_style)
        sheet.merge_range('E2:G2', 'Salary Advance', header_style)
        sheet.merge_range('H2:J2', 'Loans', header_style)
        sheet.merge_range('K2:M2', 'Housing Advance', header_style)

        headers = [
            "Employee Code",
            "Employee Name",
            "Department",
            "Branch",
            "Debit", "Credit", "Balance",
            "Debit", "Credit", "Balance",
            "Debit", "Credit", "Balance"
        ]
        sheet.write_row(2, 0, headers, header_style)

        date_from = data.get('date_from')
        date_to = data.get('date_to')
        employee_id = data.get('employee_id')
        department_id = data.get('department_id')

        domain = []
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if employee_id:
            domain.append(('employee_id', '=', employee_id))
        if department_id:
            domain.append(('department_id', '=', department_id))

        # --- Salary Advance Debit ---
        salary_advances = self.env['salary.advance'].read_group(
            domain=domain,
            fields=['employee_id', 'amount:sum'],
            groupby=['employee_id']
        )
        salary_advance_debit_dict = {
            rec['employee_id'][0]: rec['amount'] for rec in salary_advances if rec['employee_id']
        }

        payslip_domain = []
        if date_from:
            payslip_domain.append(('date_from', '>=', date_from))
        if date_to:
            payslip_domain.append(('date_to', '<=', date_to))
        if employee_id:
            payslip_domain.append(('employee_id', '=', employee_id))
        if department_id:
            payslip_domain.append(('employee_id.department_id', '=', department_id))

        salary_advance_credit_dict = {}
        for payslip in self.env['hr.payslip'].search(payslip_domain):
            if payslip.salary_advance:
                emp_id = payslip.employee_id.id
                salary_advance_credit_dict[emp_id] = salary_advance_credit_dict.get(emp_id,
                                                                                    0.0) + payslip.salary_advance

        loans_debit = self.env['loans'].read_group(
            domain=domain,
            fields=['employee_id', 'amount:sum'],
            groupby=['employee_id']
        )
        loans_debit_dict = {rec['employee_id'][0]: rec['amount'] for rec in loans_debit if rec['employee_id']}

        loan_line_domain = []
        if date_from:
            loan_line_domain.append(('loans_id.date', '>=', date_from))
        if date_to:
            loan_line_domain.append(('loans_id.date', '<=', date_to))
        if employee_id:
            loan_line_domain.append(('loans_id.employee_id', '=', employee_id))
        if department_id:
            loan_line_domain.append(('loans_id.department_id', '=', department_id))
        loan_line_domain.append(('is_paid', '=', True))

        loans_credit_dict = {}
        for line in self.env['loans.line'].search(loan_line_domain):
            emp_id = line.loans_id.employee_id.id
            loans_credit_dict[emp_id] = loans_credit_dict.get(emp_id, 0.0) + line.amount

        housing_advances = self.env['housing.advance'].read_group(
            domain=domain,
            fields=['employee_id', 'amount:sum'],
            groupby=['employee_id']
        )
        housing_debit_dict = {
            rec['employee_id'][0]: rec['amount'] for rec in housing_advances if rec['employee_id']
        }

        housing_line_domain = []
        if date_from:
            housing_line_domain.append(('housing_advance_id.date', '>=', date_from))
        if date_to:
            housing_line_domain.append(('housing_advance_id.date', '<=', date_to))
        if employee_id:
            housing_line_domain.append(('housing_advance_id.employee_id', '=', employee_id))
        if department_id:
            housing_line_domain.append(('housing_advance_id.department_id', '=', department_id))
        housing_line_domain.append(('is_paid', '=', True))

        housing_credit_dict = {}
        for line in self.env['housing.advance.line'].search(housing_line_domain):
            emp_id = line.housing_advance_id.employee_id.id
            housing_credit_dict[emp_id] = housing_credit_dict.get(emp_id, 0.0) + line.amount

        all_employee_ids = set(salary_advance_debit_dict) | set(salary_advance_credit_dict) | \
                           set(loans_debit_dict) | set(loans_credit_dict) | \
                           set(housing_debit_dict) | set(housing_credit_dict)

        employees = self.env['hr.employee'].browse(list(all_employee_ids)).sorted(
            key=lambda e: e.employee_number or e.name
        )

        row = 3
        for emp in employees:
            s_debit = salary_advance_debit_dict.get(emp.id, 0.0)
            s_credit = salary_advance_credit_dict.get(emp.id, 0.0)
            s_balance = s_debit - s_credit

            l_debit = loans_debit_dict.get(emp.id, 0.0)
            l_credit = loans_credit_dict.get(emp.id, 0.0)
            l_balance = l_debit - l_credit

            h_debit = housing_debit_dict.get(emp.id, 0.0)
            h_credit = housing_credit_dict.get(emp.id, 0.0)
            h_balance = h_debit - h_credit

            sheet.write(row, 0, emp.employee_number or '', number_style)
            sheet.write(row, 1, emp.name, cell_style)
            sheet.write(row, 2, emp.department_id.name or '', cell_style)
            sheet.write(row, 3, emp.location.name if hasattr(emp, 'location') and emp.location else '', cell_style)

            sheet.write(row, 4, s_debit, number_style)
            sheet.write(row, 5, s_credit, number_style)
            sheet.write(row, 6, s_balance, number_style)

            sheet.write(row, 7, l_debit, number_style)
            sheet.write(row, 8, l_credit, number_style)
            sheet.write(row, 9, l_balance, number_style)

            sheet.write(row, 10, h_debit, number_style)
            sheet.write(row, 11, h_credit, number_style)
            sheet.write(row, 12, h_balance, number_style)

            row += 1

        if row > 3:
            row += 1
            sheet.write(row, 0, "TOTAL", header_style)
            for col in range(1, 4):
                sheet.write(row, col, "", header_style)

            total_s_debit = sum(salary_advance_debit_dict.values())
            total_s_credit = sum(salary_advance_credit_dict.values())
            total_s_balance = total_s_debit - total_s_credit

            total_l_debit = sum(loans_debit_dict.values())
            total_l_credit = sum(loans_credit_dict.values())
            total_l_balance = total_l_debit - total_l_credit

            total_h_debit = sum(housing_debit_dict.values())
            total_h_credit = sum(housing_credit_dict.values())
            total_h_balance = total_h_debit - total_h_credit

            sheet.write(row, 4, total_s_debit, header_style)
            sheet.write(row, 5, total_s_credit, header_style)
            sheet.write(row, 6, total_s_balance, header_style)

            sheet.write(row, 7, total_l_debit, header_style)
            sheet.write(row, 8, total_l_credit, header_style)
            sheet.write(row, 9, total_l_balance, header_style)

            sheet.write(row, 10, total_h_debit, header_style)
            sheet.write(row, 11, total_h_credit, header_style)
            sheet.write(row, 12, total_h_balance, header_style)

