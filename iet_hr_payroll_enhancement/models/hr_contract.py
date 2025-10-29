# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta


class HRContractInherit(models.Model):
    _inherit = 'hr.contract'

    food_allowance = fields.Monetary(string='Food allowance')
    phone_allowance = fields.Monetary(string='Phone allowance')
    natural_of_work_allowance = fields.Monetary(string='Natural Of Work allowance')
    social_insurance_allowance = fields.Monetary(string='Social Insurance Allowance')
    total_salary = fields.Monetary(string='Total Salary', compute='_compute_total_salary', store=True)
    base_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    country_code = fields.Char(related='company_country_id.code', string='Saudi Company Country Code')
    contract_history_line_ids = fields.One2many('hr.contract.history.line', 'contract_id')
    # custom_transportation_allowance = fields.Monetary(string='Transportation Allowance')
    # custom_housing_allowance = fields.Monetary(string='Housing Allowance')
    housing_type_allowance = fields.Selection(
        [('housing_allowance', 'Housing Allowance Category'), ('period', 'Period'),
         ('monthly_housing', 'Monthly Housing Allowance')])
    number_of_absent_days = fields.Integer(string='Number Of Absent Days', compute='_compute_number_of_absent_days')
    wage = fields.Monetary(
        string='Wage',
        required=False,
        tracking=True,
        help="Employee's monthly gross wage.",
        group_operator="avg"
    )

    def _compute_number_of_absent_days(self):
        for contract in self:
            absences = 0.0
            payslips = self.env['hr.payslip'].search([('employee_id', '=', contract.employee_id.id),
                                                      ('date_from', '>', contract.date_start),
                                                      ('date_from', '<', contract.date_end),
                                                      ('state', 'not in', ('draft', 'cancel'))])
            if payslips:
                absences = sum(payslips.mapped('number_of_absences_days'))
            contract.number_of_absent_days = absences

    @api.depends('l10n_sa_housing_allowance', 'l10n_sa_transportation_allowance',
                  'food_allowance', 'phone_allowance', 'natural_of_work_allowance', 'wage', 'l10n_sa_other_allowances')
    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = rec.l10n_sa_housing_allowance + rec.l10n_sa_other_allowances + rec.l10n_sa_transportation_allowance + \
                               rec.food_allowance + rec.phone_allowance + rec.natural_of_work_allowance + rec.wage

    def compute_salary_from_history(self):
        for rec in self:
            print('in')
            inc_wage = 0
            dec_wage = 0
            inc_transportation_allowance = 0
            dec_transportation_allowance = 0
            inc_housing_allowance = 0
            dec_housing_allowance = 0

            inc_food_allowance = 0
            dec_food_allowance = 0

            inc_phone_allowance = 0
            dec_phone_allowance = 0

            inc_natural_of_work_allowance = 0
            dec_natural_of_work_allowance = 0

            inc_other_allowance = 0
            dec_other_allowance = 0
            for line in self.contract_history_line_ids:
                if line:
                    inc_wage += sum(line.filtered(lambda r: r.type == 'increase').mapped('wage'))
                    dec_wage += sum(line.filtered(lambda r: r.type == 'decrease').mapped('wage'))

                    inc_transportation_allowance += sum(
                        line.filtered(lambda r: r.type == 'increase').mapped('transportation_allowance'))
                    dec_transportation_allowance += sum(
                        line.filtered(lambda r: r.type == 'decrease').mapped('transportation_allowance'))

                    inc_housing_allowance += sum(
                        line.filtered(lambda r: r.type == 'increase').mapped('housing_allowance'))
                    dec_housing_allowance += sum(
                        line.filtered(lambda r: r.type == 'decrease').mapped('housing_allowance'))

                    inc_food_allowance += sum(line.filtered(lambda r: r.type == 'increase').mapped('food_allowance'))
                    dec_food_allowance += sum(line.filtered(lambda r: r.type == 'decrease').mapped('food_allowance'))

                    inc_phone_allowance += sum(line.filtered(lambda r: r.type == 'increase').mapped('phone_allowance'))
                    dec_phone_allowance += sum(line.filtered(lambda r: r.type == 'decrease').mapped('phone_allowance'))

                    inc_natural_of_work_allowance += sum(line.filtered(lambda r: r.type == 'increase').mapped('natural_of_work_allowance'))
                    dec_natural_of_work_allowance += sum(line.filtered(lambda r: r.type == 'decrease').mapped('natural_of_work_allowance'))

                    inc_other_allowance += sum(line.filtered(lambda r: r.type == 'increase').mapped('other_allowance'))
                    dec_other_allowance += sum(line.filtered(lambda r: r.type == 'decrease').mapped('other_allowance'))

            total_wage = inc_wage - dec_wage
            total_transportation_allowance = inc_transportation_allowance - dec_transportation_allowance
            total_housing_allowance = inc_housing_allowance - dec_housing_allowance
            total_food_allowance = inc_food_allowance - dec_food_allowance
            total_phone_allowance = inc_phone_allowance - dec_phone_allowance
            total_natural_of_work_allowance = inc_natural_of_work_allowance - dec_natural_of_work_allowance
            total_other_allowance = inc_other_allowance - dec_other_allowance

            rec.wage = total_wage
            rec.l10n_sa_transportation_allowance = total_transportation_allowance
            if rec.housing_type_allowance != 'monthly_housing':
                rec.l10n_sa_housing_allowance = total_housing_allowance
            rec.food_allowance = total_food_allowance
            rec.phone_allowance = total_phone_allowance
            rec.natural_of_work_allowance = total_natural_of_work_allowance
            rec.l10n_sa_other_allowances = total_other_allowance
            rec._compute_total_salary()


class HRContractHistoryInherit(models.Model):
    _name = 'hr.contract.history.line'

    contract_id = fields.Many2one('hr.contract')
    date = fields.Date(string='Date')
    total_salary = fields.Float(string='Total Salary')
    wage = fields.Float(string='Wage')
    transportation_allowance = fields.Float()
    food_allowance = fields.Float()
    phone_allowance = fields.Float()
    natural_of_work_allowance = fields.Float()
    other_allowance = fields.Float()
    housing_allowance = fields.Float(string='Housing Allowance')
    employee_id = fields.Many2one('hr.employee', string="Employee", related='contract_id.employee_id', store=True)

    type = fields.Selection([('increase', 'Increase'), ('decrease', 'Decrease'),
                             ], default='increase')

