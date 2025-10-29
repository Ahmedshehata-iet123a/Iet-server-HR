# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AccMoveLine(models.Model):
    _inherit = 'account.move.line'

    employee_analytic_id = fields.Many2one('employee.analytic.report', string="Employee Analytic")
    employee_id = fields.Many2one(related="employee_analytic_id.employee_id", string="Employee")
    x_balance = fields.Monetary(compute='_compute_debit_credit_balance_x', string='Balance')

    @api.depends('debit','credit')
    def _compute_debit_credit_balance_x(self):
        for record in self:
            record.x_balance = record.credit - record.debit



class EmployeeReport(models.Model):
    _name = 'employee.analytic.report'
    rec_name = 'employee_id'
    _order = 'name desc'
    # _order = 'name asc'

    name = fields.Char(readonly=True, copy=False, default='New', tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)

    # use auto_join to speed up name_search call
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, auto_join=True, tracking=True, check_company=True)

    balance = fields.Monetary(compute='_compute_debit_credit_balance', string='Balance')
    debit = fields.Monetary(compute='_compute_debit_credit_balance', string='Debit')
    credit = fields.Monetary(compute='_compute_debit_credit_balance', string='Credit')

    def _compute_debit_credit_balance(self):
        for record in self:
            record.debit = record.credit = record.balance = 0.0
            if record.employee_id:
                record.debit = sum(self.env['account.move.line'].search([('move_id.state','=','posted'),('employee_analytic_id','=',record.id)]).mapped('debit'))
                record.credit = sum(self.env['account.move.line'].search([('move_id.state','=','posted'),('employee_analytic_id','=',record.id)]).mapped('credit'))
                record.balance = record.credit - record.debit

    emp_analytic_lines_counter = fields.Integer(string='Analytic Lines', compute='_compute_analytic_lines')

    def update_employee_reports(self):
        reports = self.search([], order="name")
        for report in reports:
            if 'False' in report.name:
                # Get the next sequence value
                new_sequence = str(self.env['ir.sequence'].next_by_code('emp.report.seq'))
                # Replace "False" with the new sequence
                updated_name = report.name.replace("False", new_sequence)
                report.name = updated_name

    def _compute_analytic_lines(self):
        for rec in self:
            rec.emp_analytic_lines_counter = self.env['account.move.line'].search_count([('move_id.state','=','posted'),('employee_analytic_id', '=', rec.id)])

    def action_open_analytic_lines(self):
        related_requests = self.env['account.move.line'].search([('move_id.state','=','posted'),('employee_analytic_id', '=', self.id)])
        action = self.sudo().env.ref('iet_hr_employee_enhancement.account_move_line_preview_action').read()[0]
        action['domain'] = [('id', 'in', related_requests.ids)]

        return action

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            employee_name = self.env['hr.employee'].browse(vals.get('employee_id')).name
            vals['name'] = str(self.env['ir.sequence'].next_by_code('emp.report.seq')) + ' [%s]' % employee_name or 'New'
        result = super(EmployeeReport, self).create(vals)
        return result

    @api.model
    def action_to_create_new_analytic_for_emp(self):
        all_emp = self.env['hr.employee'].search([])
        all_analytic = self.env['employee.analytic.report'].search([])
        # print('all_contracts=', all_emp, all_analytic)
        all_ids= []
        our_emp_ids= []
        if all_analytic:
            for rec in all_analytic:
                all_ids.append(rec.employee_id.id)
        # print('all_ids=', all_ids)
        if all_emp.ids:
            for e in all_emp.ids:
                if e not in  all_ids:
                    # print(e)
                    our_emp_ids.append(e)
        # print('our_emp_ids==', our_emp_ids)
        if our_emp_ids:
            for f in our_emp_ids:
                module_metadata = {
                    'employee_id': f,
                }
                self.env['employee.analytic.report'].create(module_metadata)
        # to asign employee_custom_analytic_id to old records we will call this def
        all_emp._compute_employee_custom_analytic_id()

    def unlink(self):
        for rec in self:
            if rec.balance != 0:
                raise ValidationError('You can`t delete this record, whose balance is greater or less than zero')
        return super(EmployeeReport, self).unlink()

