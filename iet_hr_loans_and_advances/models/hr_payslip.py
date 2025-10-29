# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class HrPaysLipInherit(models.Model):
    _inherit = 'hr.payslip'

    loans_line_ids = fields.One2many(comodel_name="loans.line", inverse_name="loans_payslip_id",
                                     required=False, compute='get_loan_ids')
    total_loans = fields.Float(compute='get_loan_ids', readonly=False, store=True)
    loans = fields.Float(string="Loans", compute='_compute_loans')
    total_unpaid_loans = fields.Float(string="Total unpaid loans", compute='_compute_total_unpaid_loans')

    housing_advance_lines_ids = fields.One2many(comodel_name="housing.advance.line", inverse_name="housing_advance_payslip_id",
                                     required=False, compute='get_housing_advance_ids')
    total_housing_advance = fields.Float(compute='get_housing_advance_ids', readonly=False, store=True)
    housing_advance = fields.Float(string="Housing Advance", compute='_compute_housing_advance')
    total_unpaid_housing_advance = fields.Float(string="Total unpaid housing_advance", compute='_compute_total_unpaid_housing_advance')

    salary_advance_ids = fields.One2many(comodel_name="salary.advance", inverse_name="salary_advance_id", string="",
                                         required=False, compute='get_salary_advance_ids')
    salary_advance = fields.Float(string="Salary Advance", compute='get_salary_advance_ids')
    car_loans = fields.Float(string="Car Loans", required=False, )
    other_loans = fields.Float(string="Other Loans", required=False, )

    custom_total_deductions = fields.Float("Total Deductions", compute='_custom_total_deductions')

    def action_payslip_unpaid(self):
        pass

    @api.depends('loans', 'salary_advance', 'housing_advance')
    def _custom_total_deductions(self):
        for rec in self:
            loans = rec.loans or 0.0
            # violations = rec.violations or 0.0
            salary_advance = rec.salary_advance or 0.0
            housing_advance = rec.housing_advance or 0.0
            rec.custom_total_deductions = loans + salary_advance

    @api.depends('employee_id', 'date_from', 'date_to', 'employee_id.contract_id.wage')
    def get_loan_ids(self):
        for rec in self:
            previous_payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '!=', 'draft'),
                ('date_to', '<', rec.date_from),
            ])
            total_previous_unpaid_loans = sum(previous_payslips.mapped('total_unpaid_loans')) or 0

            loans = self.env['loans.line'].search([
                ('loans_id.employee_id', '=', rec.employee_id.id),
                ('loans_id.state', '=', 'paid'),
                ('name', '<=', rec.date_to),
                ('name', '>=', rec.date_from),
            ])
            if loans:
                rec.write({
                    'loans_line_ids': [(6, 0, [loan.id for loan in loans])]
                })
            else:
                rec.loans_line_ids = False

            total_current_loans = sum(
                rec.loans_line_ids.mapped('amount')) if rec.loans_line_ids else 0
            rec.total_loans = total_current_loans + total_previous_unpaid_loans

    # @api.depends('employee_id', 'date_from', 'date_to', )
    # def get_loan_ids(self):
    #     self.loans_line_ids = False
    #     self.loans = 0
    #     for rec in self:
    #         loans = self.env['loans'].search([
    #             ('employee_id', '=', rec.employee_id.id),
    #             ('state', '=', 'paid'),
    #             ('loans_ids', '!=', False),
    #         ])
    #         if loans:
    #             rec.loans_line_ids = loans.loans_ids.filtered(lambda loan: loan.name >= rec.date_from and loan.name <= rec.date_to and loan.delay != True and loan.is_created != True).ids
    #             rec.loans = sum(list(rec.loans_line_ids.mapped('amount'))) if rec.loans_line_ids else 0
    #         amount = 0
    #         for l in loans.loans_ids:
    #             if l.is_paid == False:
    #                 amount += l.amount
    #             # rec.total_unpaid_loans = amount
    #
    #         rec.total_unpaid_loans = amount

    @api.depends('total_loans', 'employee_id.contract_id.wage')
    def _compute_loans(self):
        for rec in self:
            total_loans = rec.total_loans
            if total_loans <= (rec.employee_id.contract_id.wage / 4):
                rec.loans = total_loans
            else:
                rec.loans = rec.employee_id.contract_id.wage / 4

    @api.depends('total_loans', 'loans')
    def _compute_total_unpaid_loans(self):
        for rec in self:
            if rec.total_loans and rec.loans:
                rec.total_unpaid_loans = rec.total_loans - rec.loans
            else:
                rec.total_unpaid_loans = 0

    @api.depends('employee_id', 'date_from', 'date_to', 'employee_id.contract_id.wage')
    def get_housing_advance_ids(self):
        for rec in self:
            previous_payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '!=', 'draft'),
                ('date_to', '<', rec.date_from),
            ])
            total_previous_unpaid_housing_advance = sum(previous_payslips.mapped('total_unpaid_housing_advance')) or 0

            housing_advance = self.env['housing.advance.line'].search([
                ('housing_advance_id.employee_id', '=', rec.employee_id.id),
                ('housing_advance_id.state', '=', 'paid'),
                ('name', '<=', rec.date_to),
                ('name', '>=', rec.date_from),
            ])
            if housing_advance:
                rec.write({
                    'housing_advance_lines_ids': [(6, 0, [housing_advance.id for housing_advance in housing_advance])]
                })
            else:
                rec.housing_advance_lines_ids = False

            total_current_housing_advance = sum(
                rec.housing_advance_lines_ids.mapped('amount')) if rec.housing_advance_lines_ids else 0
            rec.total_housing_advance = total_current_housing_advance + total_previous_unpaid_housing_advance


    @api.depends('total_housing_advance', 'employee_id.contract_id.wage')
    def _compute_housing_advance(self):
        for rec in self:
            total_housing_advance = rec.total_housing_advance
            if total_housing_advance <= (rec.employee_id.contract_id.wage / 4):
                rec.housing_advance = total_housing_advance
            else:
                rec.housing_advance = rec.employee_id.contract_id.wage / 4

    @api.depends('total_housing_advance', 'housing_advance')
    def _compute_total_unpaid_housing_advance(self):
        for rec in self:
            if rec.total_housing_advance and rec.housing_advance:
                rec.total_unpaid_housing_advance = rec.total_housing_advance - rec.housing_advance
            else:
                rec.total_unpaid_housing_advance = 0

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_salary_advance_ids(self):
        for rec in self:
            rec.salary_advance_ids = False
            salary_advance = self.env['salary.advance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('deduction_date', '<=', rec.date_to),
                ('deduction_date', '>=', rec.date_from),
            ])
            if salary_advance:
                rec.write({
                    'salary_advance_ids': [(6, 0, [advance.id for advance in salary_advance])]
                })

            else:
                rec.salary_advance_ids = False
            rec.salary_advance = sum(rec.salary_advance_ids.mapped('amount')) if rec.salary_advance_ids else 0

    def compute_sheet(self):
        self.get_loan_ids()
        self.get_housing_advance_ids()
        # self.get_violations_line_ids()
        self.get_salary_advance_ids()
        return super().compute_sheet()

    def action_payslip_paid(self):
        print('action_payslip_paid')
        res = super(HrPaysLipInherit, self).action_payslip_paid()
        for rec in self:
            loans = self.env['loans'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('loans_ids', '!=', False),
            ])
            if loans:
                the_line = loans.loans_ids.filtered(
                    lambda loan: loan.name >= rec.date_from and loan.name <= rec.date_to and
                                 loan.delay != True and loan.is_created != True and
                                 loan.is_paid != True)
                print('the_line', the_line)
                if the_line:
                    if rec.state == 'paid':
                        print('rec.state ', rec.state)
                        the_line.is_paid = True

            housing_advance = self.env['housing.advance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('housing_advance_lines_ids', '!=', False),
            ])
            if housing_advance:
                the_line = housing_advance.housing_advance_lines_ids.filtered(
                    lambda housing_advance: housing_advance.name >= rec.date_from and housing_advance.name <= rec.date_to and
                                 housing_advance.delay != True and housing_advance.is_created != True and
                                 housing_advance.is_paid != True)
                print('the_line', the_line)
                if the_line:
                    if rec.state == 'paid':
                        print('rec.state ', rec.state)
                        the_line.is_paid = True


                # print('the_line.is_paid==', the_line.is_paid)
            # violations = self.env['violations'].search([
            #     ('employee_id', '=', rec.employee_id.id),
            #     ('state', '=', 'paid'),
            #     ('violations_ids', '!=', False),
            # ])
            # if violations:
            #     the_violations = violations.violations_ids.filtered(
            #         lambda v: v.name >= rec.date_from and v.name <= rec.date_to and
            #                   v.delay != True and v.is_created != True and v.is_paid != True)
            #     if the_violations:
            #         if rec.state == 'paid':
            #             the_violations.is_paid = True


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    is_loan = fields.Boolean(string="Is Loan", )
    is_salary_advance = fields.Boolean(string="Is Salary Advance", )
    is_housing_advance = fields.Boolean(string="Is Housing Advance", )
    account_ids = fields.Many2one('account.account', string='Debit Account', )
    account_idd = fields.Many2one('account.account', string='Credit Account', )

