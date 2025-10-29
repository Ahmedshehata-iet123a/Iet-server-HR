# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TimeOffReportView(models.AbstractModel):
    _name = "report.iet_hr_holidays_enhancement.leave_view"
    _description = "Time Off Report"

    def get_total_days_paid_and_unpaid(self, docids):
        hr_leave = self.env['hr.leave'].search([('id', '=', docids)])
        for rec in hr_leave:
            if len(rec.employee_ids) == 1:
                total_days = 0
                if hr_leave:
                    total_days = hr_leave.number_of_days
                    if hr_leave.related_leave_id:
                        total_days = hr_leave.number_of_days + hr_leave.related_leave_id.number_of_days
                return total_days
            else:
                return 0

    def get_last_time_off(self, docids):
        hr_leave = self.env['hr.leave'].search([('id', '=', docids)])
        if hr_leave:
            for rec in hr_leave:
                if len(rec.employee_ids) == 1:
                    hr22_leave22 = self.env['hr.leave'].search([('employee_id', '=', rec.employee_ids.id), ('id', '!=', docids)])
                    if hr22_leave22:
                        date = hr22_leave22[0].request_date_from
                        return date
                    else:
                        return 0
        else:
            return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        docs2 = []
        docs3 = []
        count = 1
        return_date = ''
        company_id = self.env.user.company_id
        hr_leave = self.env['hr.leave'].search([('id', '=', docids)])
        for line in hr_leave.employee_ids:
            docs.append({
                # 'pin_no': line.pin,
                'pin_no': line.custom_employee_pin_number,
                'employee_name': line.name,
                'passport_no': line.passport_id,
                'passport_end_date': line.end_date_passport,
                'visa_no': line.visa_no,
                'country_name': line.country_id.name,
                'visa_expire': line.visa_expire,
                'residency': line.residency,
                'identification': line.identification_id,
                'end_date_identification': line.end_date_identification,
                'residency_date': line.residency_date,
                'department_name': line.department_id.name,
                'job_title': line.job_title,

            })
            hr_contract = self.env['hr.contract.history'].search([('employee_id', '=', line.id)])
            hr_leave2 = self.env['hr.leave'].search([('employee_id', '=', line.id)], order='return_date asc', limit=1)
            if hr_leave2.id != hr_leave.id:
                return_date = hr_leave2.return_date
            for line2 in hr_contract.contract_ids:
                docs2.append({
                    'contract_name': line2.name,
                    'date_start': line2.date_start,
                    'date_end': line2.date_end,
                    'count': count,

                })
                count += 1
            total_days_paid_and_unpaid = self.get_total_days_paid_and_unpaid(docids)
            last_date = self.get_last_time_off(docids)
            if last_date == 0:
                last_date = '__'
            for line3 in hr_leave:
                docs3.append({
                    'holiday_name': line3.holiday_status_id.name,
                    'number_of_days': line3.number_of_days,
                    'total_days_paid_and_unpaid': total_days_paid_and_unpaid,
                    'last_date': last_date,
                    'request_date_from': line3.request_date_from,
                    'request_date_to': line3.request_date_to,
                    'amount': line3.amount,

                })

        return {
            'docs': docs,
            'docs2': docs2,
            'docs3': docs3,
            'company_logo': company_id.logo,
            'return_date': return_date,
            'date': hr_leave.date_now,

        }
