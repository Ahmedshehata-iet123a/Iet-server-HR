# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class HousingAdvance(models.Model):
    _name = 'housing.advance'
    _description = 'housing_advance_Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    state = fields.Selection([("draft", "To HR Validate"),
                              ("financial_manager", "To Finance Approval"),
                              ("confirm", "Approved"),
                              ("paid", "Paid"),
                              ("paid2", "To Reconcile"),
                              ("reconcile", "Reconciled"),
                              ("rejected", "Rejected")],
                             readonly=True,
                             default="draft",
                             tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True, default=fields.Date.today)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True, default=fields.Date.today)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    employee_number = fields.Char(related="employee_id.employee_number", tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    no_of_installment = fields.Integer(string="No Of Installment", tracking=True, default=1)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    housing_advance_lines_ids = fields.One2many('housing.advance.line', 'housing_advance_id', string="", )
    # reason = fields.Text(string="Reason", tracking=True)
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        tracking=True,
        default=lambda self: self.env['account.journal'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param('iet_hr_loans_and_advances.journal_id_for_housing_advance',
                                                                 default=0))
        )
    )

    account_id = fields.Many2one(
        'account.account',
        string='Debit Account',
        tracking=True,
        default=lambda self: self.env['account.account'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param('iet_hr_loans_and_advances.account_debit_for_housing_advance',
                                                                 default=0))
        )
    )

    account_idd = fields.Many2one(
        'account.account',
        string='Credit Account',
        tracking=True,
        default=lambda self: self.env['account.account'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param('iet_hr_loans_and_advances.account_credit_for_housing_advance',
                                                                 default=0))
        )
    )

    journal_id_reconcile_account = fields.Many2one(
        'account.journal',
        string='Journal',
        tracking=True,
        default=lambda self: self.env['account.journal'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param(
                'iet_hr_loans_and_advances.journal_id_reconcile_for_housing_advance', default=0))
        )
    )

    debit_reconcile_account = fields.Many2one(
        'account.account',
        string='Debit Account',
        tracking=True,
        default=lambda self: self.env['account.account'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param('iet_hr_loans_and_advances.debit_reconcile_for_housing_advance',
                                                                 default=0))
        )
    )

    credit_reconcile_account = fields.Many2one(
        'account.account',
        string='Credit Account',
        tracking=True,
        default=lambda self: self.env['account.account'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param('iet_hr_loans_and_advances.credit_reconcile_for_housing_advance',
                                                                 default=0))
        )
    )

    payslip_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    journal_entry_id_for_reconcile = fields.Many2one('account.move', string='', copy=False, readonly=True)

    amount_not_paid = fields.Float(string="amount not paid", compute='_compute_amount_not_paid')
    employees_customs_analytics_id = fields.Many2one('employee.analytic.report', string="Employee Analytic",
                                                     related='employee_id.employee_custom_analytic_id')
    barcode_for_housing_advance = fields.Char(string="Employee Badge ID", related='employee_id.barcode')
    identification_for_housing_advance = fields.Char(string="Identification No",
                                                     related='employee_id.identification_id', )
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.company, )

    @api.onchange('amount')
    def _onchange_amount(self):
        for rec in self:
            housing_allowance = rec.employee_id.contract_id.l10n_sa_housing_allowance
            if rec.amount > housing_allowance * 6:
                rec.amount = housing_allowance * 6
                return {
                    'warning': {
                        'title': 'High Amount value',
                        'message': "The maximum value that can be entered is six times the employee's Housing Allowance."
                    }
                }

    @api.onchange('no_of_installment')
    def _onchange_no_of_installment(self):
        for rec in self:
            if rec.no_of_installment > 6:
                rec.no_of_installment = 6
                return {
                    'warning': {
                        'title': 'High No Of Installment value',
                        'message': 'The maximum value that can be entered is 6.'
                    }
                }

    def unlink(self):
        error_message = _('You cannot delete a housing advance which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.env.user.has_group('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(HousingAdvance, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('housing_advance.code') or 'New'
        result = super(HousingAdvance, self).create(vals)
        return result

    def paid2(self):
        for rec in self:
            rec.state = 'paid2'

    def action_compute(self):
        for rec in self:
            list = []
            count = 0
            housing_advance_lines = []
            for line in rec.housing_advance_lines_ids:
                if not line.is_created:
                    if not line.delay:
                        list.append(line.name)
                    else:
                        count += 1
                        line.is_created = True
            max_date = max(list)
            new_date = max_date + relativedelta(months=1)
            for i in range(count):
                housing_advance_lines.append((0, 0, {
                    'name': new_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                new_date = new_date + relativedelta(months=1)

            rec.housing_advance_lines_ids = housing_advance_lines

    def compute_installment(self):
        for rec in self:
            housing_advance_lines = []
            no_install = rec.no_of_installment
            rec.housing_advance_lines_ids = False
            date_date = rec.deduction_date
            for line in range(no_install):
                housing_advance_lines.append((0, 0, {
                    'name': date_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                date_date = date_date + relativedelta(months=1)
            rec.housing_advance_lines_ids = housing_advance_lines

    def validate_action(self):
        for rec in self:
            rec.state = 'financial_manager'
        self.compute_installment()

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def financial_manager(self):
        for rec in self:
            rec.state = 'confirm'

    # def general_manager(self):
    #     for rec in self:
    #         rec.state = 'confirm'

    def paid(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'ref': rec.name,
                'date': rec.deduction_date,
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount,
                    'employee_analytic_id': rec.employees_customs_analytics_id.id,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'paid'

    @api.depends('housing_advance_lines_ids')
    def _compute_amount_not_paid(self):
        for rec in self:
            rec.amount_not_paid = 0
            if rec.housing_advance_lines_ids:
                amount_not_p = 0
                for i in rec.housing_advance_lines_ids:
                    if i.is_paid == False:
                        amount_not_p += i.amount
                rec.amount_not_paid = amount_not_p

    def reconcile_amount(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'ref': rec.name,
                'date': rec.deduction_date,
                'journal_id': self.journal_id_reconcile_account.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.debit_reconcile_account.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount_not_paid,
                    'employee_analytic_id': rec.employees_customs_analytics_id.id,
                }), (0, 0, {
                    'account_id': rec.credit_reconcile_account.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount_not_paid,
                })],
            })
            rec.journal_entry_id_for_reconcile = invoice.id
            rec.state = 'reconcile'
            if rec.housing_advance_lines_ids:
                for l in rec.housing_advance_lines_ids:
                    l.is_paid = True

    def rejected(self):
        for rec in self:
            rec.state = 'rejected'

    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def _check_exist_employee_id(self):
        print('_check_exist_employee_id')
        for sc in self:
            housing_advance = self.env['housing.advance'].search(
                [('employee_id', '=', sc.employee_id.id), ('state', '=', 'paid'),
                 ('housing_advance_lines_ids', '!=', False)])
            if housing_advance:
                the_lhousing_advance_is_not_paid = housing_advance.housing_advance_lines_ids.filtered(
                    lambda housing_advance: housing_advance.is_paid != True)
                if the_lhousing_advance_is_not_paid:
                    raise ValidationError("Please pay all installments for this employee's first")
                else:
                    continue
            else:
                continue


class HousingAddvanceLine(models.Model):
    _name = 'housing.advance.line'
    _description = 'housing_advance_line'

    name = fields.Date('Payment Date')
    amount = fields.Float('Amount')
    housing_advance_payslip_id = fields.Many2one('hr.payslip', string='')
    housing_advance_id = fields.Many2one('housing.advance', string='')
    delay = fields.Boolean()
    is_created = fields.Boolean()
    is_paid = fields.Boolean(string='In payslip', readonly=True)

    # readonly = True

    @api.onchange('delay')
    def get_checkbox_match(self):
        for rec in self:
            rec.is_paid = rec.delay
