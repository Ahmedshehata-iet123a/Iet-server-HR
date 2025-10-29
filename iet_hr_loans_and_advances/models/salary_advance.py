# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SalaryAdvance(models.Model):
    _name = 'salary.advance'
    _description = 'salary advance Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def get_journal(self):
        journal = self.env['account.journal'].sudo().search([('is_salary_advance', '=', True)], limit=1).id
        return journal

    state = fields.Selection([("draft", "To HR Validate"),
                              ("financial_manager", "To Finance Approval"),
                              ("general_manager", "To General Approval"),
                              ("confirm", "Approved"),
                              ("paid", "Paid"),
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
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        tracking=True,
        default=lambda self: self.env['account.journal'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param(
                'iet_hr_loans_and_advances.journal_id_for_salary_advances',
                default=0))
        )
    )

    account_id = fields.Many2one(
        'account.account',
        string='Debit Account',
        tracking=True,
        default=lambda self: self.env['account.account'].browse(
            int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'iet_hr_loans_and_advances.account_debit_for_salary_advances',
                    default=0))
        )
    )

    account_idd = fields.Many2one(
        'account.account',
        string='Credit Account',
        tracking=True,
        default=lambda self: self.env['account.account'].browse(
            int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'iet_hr_loans_and_advances.account_credit_for_salary_advances',
                    default=0))
        )
    )
    barcode_for_advance = fields.Char(string="Employee Badge ID", related='employee_id.barcode')
    # barcode_for_advance = fields.Char(string="Employee Badge ID")
    identification_for_advance = fields.Char(string="Identification No", related='employee_id.identification_id', )
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.company, )
    emp_customs_analytic_id = fields.Many2one('employee.analytic.report', string="Employee Analytic",
                                              related='employee_id.employee_custom_analytic_id')
    reason = fields.Text(string="Reason", tracking=True)
    salary_advance_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    type = fields.Many2one('type.loan.advance')

    def unlink(self):
        error_message = _('You cannot delete a Advance which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.env.user.has_group('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(SalaryAdvance, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('salary.advance') or 'New'
        result = super(SalaryAdvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                rec.account_id = False
                rec.account_idd = False

    def validate_action(self):
        for rec in self:
            rec.state = 'financial_manager'

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def financial_manager(self):
        for rec in self:
            rec.state = 'general_manager'

    def general_manager(self):
        for rec in self:
            rec.state = 'confirm'

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
                    'employee_analytic_id': rec.emp_customs_analytic_id.id,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'paid'

    def rejected(self):
        for rec in self:
            rec.state = 'rejected'

    @api.onchange('amount')
    def _onchange_amount(self):
        # print('_onchange_amount')
        for rec in self:
            if rec.employee_id:
                hr_contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                              ('state', '=', 'open')], limit=1)
