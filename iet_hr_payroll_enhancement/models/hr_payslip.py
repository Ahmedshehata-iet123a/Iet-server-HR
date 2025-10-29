# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HRPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    # accrual_leave = fields.Float(string='Accrual Leave', related='employee_id.accrual_leave')
    employee_number = fields.Char(related="employee_id.employee_number", tracking=True)
    accrual_leave = fields.Float(string='Accrual Leave', related='employee_id.amount_of_leave_days_balance')
    show_last_payslip = fields.Boolean(string="Show Basic In Annual")

    def action_print_payslip(self):
        return self.env.ref('iet_hr_payroll_enhancement.payroll_report_action').report_action(self)

    number_of_absences_days = fields.Float()
    amount_of_absences = fields.Float(compute='_compute_amounts_days', store=True)
    number_of_penalties_days = fields.Float()
    amount_of_penalties = fields.Float(compute='_compute_amounts_days', store=True)

    customs_attendances = fields.Float(string="Attendances")
    amount_of_attendances = fields.Float(string="Amount of Attendances", compute='_compute_amount_of_attendances',
                                         store=True)

    overtime_hours = fields.Float(string="Overtime Hours", store=True)
    overtime_amount = fields.Float(string="Overtime Amount", compute='_compute_overtime_amount', store=True)

    # @api.model_create_multi
    # def create(self, values):
    #     res = super(HRPayslipInherit, self).create(values)
    #     return_vacation = self.env['return.vacation'].search([('return_date', '>', res.date_from),
    #                                                           ('time_off_type_id.name', '=', 'Annual leave'),
    #                                                           ('employee_id', '=', res.employee_id.id),
    #                                                           ('state', '=', 'approved'), ],
    #                                                          order='return_date desc', limit=1)
    #     if return_vacation:
    #         res.date_from = return_vacation.return_date
    #     return res
    @api.model_create_multi
    def create(self, values):
        # Create records and store the results
        created_records = super(HRPayslipInherit, self).create(values)

        # Prepare to update each created record
        for record in created_records:
            return_vacation = self.env['return.vacation'].search([
                ('return_date', '>', record.date_from),
                ('time_off_type_id.name', '=', 'Annual leave'),
                ('employee_id', '=', record.employee_id.id),
                ('state', '=', 'approved')
            ], order='return_date desc', limit=1)

            if return_vacation:
                record.date_from = return_vacation.return_date

        return created_records

    @api.onchange('employee_id')
    def _onchange_employee_id_to_compute_start_date(self):
        for rec in self:
            return_vacation = self.env['return.vacation'].search([('return_date', '>', rec.date_from),
                                                                  ('time_off_type_id.name', '=', 'Annual leave'),
                                                                  ('employee_id', '=', rec.employee_id.id),
                                                                  ('state', '=', 'approved'), ],
                                                                 order='return_date desc', limit=1)
            if return_vacation:
                rec.date_from = return_vacation.return_date

    @api.depends('customs_attendances', 'employee_id.contract_id.total_salary')
    def _compute_amount_of_attendances(self):
        for rec in self:
            rec.amount_of_attendances = 0
            if rec.customs_attendances and rec.employee_id.contract_id.total_salary:
                rec.amount_of_attendances = (rec.employee_id.contract_id.total_salary / 30) * rec.customs_attendances

    @api.depends('number_of_absences_days', 'number_of_penalties_days', 'employee_id.contract_id.total_salary',
                 'employee_id.contract_id.l10n_sa_housing_allowance','employee_id.contract_id.wage', )
    def _compute_amounts_days(self):
        for rec in self:
            rec.amount_of_absences = 0
            rec.amount_of_penalties = 0
            goci = 0
            if rec.employee_id.country_id.code == 'SA':
                goci = (rec.contract_id.wage + rec.contract_id.l10n_sa_housing_allowance) * 0.0975
            print(goci)
            if rec.contract_id:
                rec.amount_of_absences = ((
                                                  rec.contract_id.total_salary - goci) / 30) * rec.number_of_absences_days or 0.0

                rec.amount_of_penalties = ((
                                                   rec.contract_id.wage) / 30) * rec.number_of_penalties_days or 0.0

    @api.depends('overtime_hours', 'contract_id.wage', 'contract_id.total_salary')
    def _compute_overtime_amount(self):
        for rec in self:
            if rec.contract_id and rec.contract_id.wage:
                rec.overtime_amount = ((rec.contract_id.total_salary / 30 / 8) * rec.overtime_hours) + (
                            (rec.contract_id.wage / 30 / 8) * rec.overtime_hours * 0.5)
            else:
                rec.overtime_amount = 0.0

    def _action_create_account_move(self):
        res = super(HRPayslipInherit, self)._action_create_account_move()
        for slip in self:
            if slip.move_id:
                for line in slip.move_id.line_ids:
                    if line.credit > 0:  # Only for credit lines
                        line.employee_analytic_id = slip.employee_id.employee_custom_analytic_id.id
        return res
