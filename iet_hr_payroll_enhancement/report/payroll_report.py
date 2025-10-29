# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PayrollReportView(models.AbstractModel):
    _name = "report.iet_hr_payroll_enhancement.payroll_form_view"
    _description = "Payroll Customs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        payslips = self.env['hr.payslip'].search([('id', '=', docids)])
        hr_leave = self.env['hr.leave'].search([('employee_id', '=', payslips.employee_id.id)], order='last_working_date DESC', limit=1)
        for line in payslips.line_ids:
            docs.append({
                'name': line.name,
                'code': line.code,
                'category_id': line.category_id.name,
                'quantity': line.quantity,
                'rate': line.rate,
                'salary_rule_id': line.salary_rule_id.name,
                'amount': line.amount,
                'total': line.total,
            })

        return {
            'docs': docs,
            'number': payslips.number,
            'date_from': payslips.date_from,
            'date_to': payslips.date_to,
            'employee_id': payslips.employee_id.name,
            'contract_id': payslips.contract_id.name,
            'payslip_run_id': payslips.payslip_run_id.name,
            'struct_id': payslips.struct_id.name,
            'last_working_date': hr_leave.last_working_date,
            'request_date_from': hr_leave.request_date_from,


        }
