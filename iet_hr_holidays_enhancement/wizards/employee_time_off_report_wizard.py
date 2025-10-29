# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date, datetime, time



class EmployeeTimeOffReportWizard(models.TransientModel):
    # region [Initial]
    _name = 'employee.time.off.report.wizard'
    # endregion

    # region [Fields]

    employee_ids = fields.Many2many('hr.employee', string='Employees', required=False)
    department_ids = fields.Many2many('hr.department', string='Departments', required=False)
    holiday_status_ids = fields.Many2many('hr.leave.type', string='Time Off Types', required=True,
                                          domain="[('requires_allocation', '=', 'yes')]")

    # endregion

    def btn_report_pdf(self):
        for report in self:
            data = {"employees_vals": []}
            holiday_employee_vals = {}
            for holiday in report.holiday_status_ids:
                if report.employee_ids and not report.department_ids:
                    employee_ids = report.employee_ids
                elif report.employee_ids and report.department_ids:
                    employee_ids = self.env['hr.employee'].search(["|", ('department_id', 'in', report.department_ids.ids), ('id', 'in', report.employee_ids.ids), ('active', '!=', False)])
                elif not report.employee_ids and report.department_ids:
                    employee_ids = self.env['hr.employee'].search([('active', '!=', False), ('department_id', 'in', report.department_ids.ids)])
                else:
                    employee_ids = self.env['hr.employee'].search([('active', '!=', False)])
                if employee_ids:
                    for employee in employee_ids:
                        employee_vals = report.prepare_employee_values(employee, holiday)
                        data["employees_vals"].append(employee_vals)
                        holiday_employee_vals.update({(employee.id, holiday.id): employee_vals})
                    # if not report.department_ids:
                    #     report.department_ids = [(4, department) for department in
                    #                              self.env['hr.department']]
                    # if report.department_ids:
                    #     department_ids = report.department_ids
                    #     for department_id in department_ids:
                    #         employee_ids = self.env["hr.employee"].sudo().search(
                    #             [("department_id", "=", department_id.id)])
                    #         if employee_ids:
                    #             for dp_employee in employee_ids:
                    #                 # employee_id_exists = any(
                    #                 #     dt.get("employee_id") == dp_employee.id for dt in data.get("employees_vals", []))
                    #                 if not (dp_employee.id, holiday.id) in holiday_employee_vals.keys():
                    #                     # if not employee_id_exists:
                    #                     employee_vals = report.prepare_employee_values(dp_employee, holiday)
                    #                     data.setdefault("employees_vals", []).append(employee_vals)
            return self.env.ref('iet_hr_holidays_enhancement.employee_time_off_report_report').report_action(self,
                                                                                                              data=data)

    def prepare_employee_values(self, employee, holiday):
        for report in self:
            min_datetime = fields.Datetime.to_string(
                datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
            max_datetime = fields.Datetime.to_string(
                datetime.now().replace(month=12, day=31, hour=23, minute=59, second=59))
            employee_vals = {
                "employee_id": employee.id,
                "identification_number": employee.identification_id,
                "employee_number": employee.employee_number,
                "employee_name": employee.name,
                "department_name": employee.department_id.name,
                "holiday_status_name": holiday.name,
            }
            holiday_ids = self.env['hr.leave'].search([
                ("employee_id", "=", employee.id),
                ("holiday_status_id", "=", holiday.id),
                ('date_from', '>=', min_datetime),
                ('date_from', '<=', max_datetime),
                ("state", "=", "validate")
            ])
            holiday_days = 0
            holiday_status_days = 0
            if holiday_ids:
                holiday_days += sum(holiday_ids.mapped("number_of_days"))
            domain = [
                ("employee_id", "=", employee.id),
                ("holiday_status_id", "=", holiday.id),
                ("state", "=", "validate"),
            ]
            domain += ["|",
                       ("date_to", "=", False),
                       ("date_to", ">=", fields.Date.today()),
                       ]
            holiday_status_ids = self.env['hr.leave.allocation'].search(domain)
            if holiday_status_ids:
                holiday_status_days += sum(holiday_status_ids.mapped("number_of_days"))
            employee_vals.update({'holiday_status_days': holiday_status_days})
            employee_vals.update({'taken_days': holiday_days})
            employee_vals.update(
                {'remaining_days': holiday_status_days - holiday_days if holiday_status_days > 0 else 0})
            return employee_vals
