from odoo import api, fields, models, _
from datetime import datetime, date, timedelta, time
from odoo.exceptions import ValidationError
import warnings
from odoo.exceptions import ValidationError


class ReturnFromVacation(models.Model):
    _name = 'return.vacation'
    _rec_name = 'employee_id'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id')
    leave_id = fields.Many2one('hr.leave', string="Time Off", )
    description = fields.Text(string="Description", )
    expected_return_date = fields.Date(related='leave_id.request_date_to', store=True)
    return_date = fields.Date(string="Return Date", compute='get_return_date', store=True, readonly=False)
    difference_of_days = fields.Integer(compute='_compute_difference_of_days', store=True)

    time_off_types = fields.Selection([
        ('annual_vacation', 'Annual Vacation'),
        ('paid_time_off', 'Paid time off'),
        ('sick_time_off', 'Sick time off'),
        ('compensatory_days', 'Compensatory Days'),
        ('unpaid', 'Unpaid'),
    ], string='Time Off Types', )
    time_off_type_id = fields.Many2one('hr.leave.type', string="Time Off Type",related='leave_id.holiday_status_id',)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approved', 'Approved'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, default='draft')

    @api.depends('return_date', 'expected_return_date')
    def _compute_difference_of_days(self):
        for rec in self:
            if rec.return_date and rec.expected_return_date:
                rec.difference_of_days = (rec.return_date - rec.expected_return_date).days + 1

    @api.depends('leave_id')
    def get_return_date(self):
        for rec in self:
            if rec.leave_id and rec.leave_id.request_date_to:
                rec.return_date = rec.leave_id.request_date_to
            else:
                rec.return_date = False

    def action_submit(self):
        for rec in self:
            rec.state = 'submit'

    def action_manager_approve(self):
        for rec in self:
            # for emp in rec.employee_id:
            rec.employee_id.warning_employee = ''
            rec.employee_id.warning_text = ''
            rec.state = 'approved'
            if rec.time_off_type_id.name == 'Annual leave':
                rec.employee_id.is_on_vacation = False

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            if rec.time_off_type_id.name == 'Annual leave':
                rec.employee_id.is_on_vacation = False

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            if rec.time_off_type_id.name == 'Annual leave':
                rec.employee_id.is_on_vacation = False

    @api.model_create_multi
    def create(self, values):
        res = super(ReturnFromVacation, self).create(values)
        if res.employee_id:
            if res.time_off_type_id.name == 'Annual leave':
                res.employee_id.is_on_vacation = False
        return res

    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise ValidationError(_('You cannot delete the request before canceling it.'))
            if rec.time_off_type_id.name == 'Annual leave':
                if rec.employee_id.is_on_vacation == True:
                    rec.employee_id.is_on_vacation = False
        return super(ReturnFromVacation, self).unlink()
