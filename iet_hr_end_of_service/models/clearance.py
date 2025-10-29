from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import datetime
from odoo.exceptions import UserError, ValidationError



class Clearance(models.Model):
    _name = 'clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Clearance'

    name = fields.Char(tracking=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('finance_approval', 'To Finance Approval'),
        ('it_approval', 'To IT Approval'),
        ('sales_approval', 'To Sales Approval'),
        ('inventory_approval', 'To Inventory Approval'),
        ('hr_approval', 'To HR Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ], default='draft', tracking=True)

    date = fields.Date(string='Application Date', tracking=True, default=fields.Date.today())
    application_type = fields.Selection([('annual_leave', 'Annual Leave'), ('end_of_service', 'End Of Service')],
                                        tracking=True)
    annual_leave_id = fields.Many2one('hr.leave')
    resignation_request_id = fields.Many2one('resignation.request')
    employee_id = fields.Many2one('hr.employee', tracking=True)
    employee_number = fields.Char(related="employee_id.employee_number", tracking=True)
    job_position = fields.Char(related="employee_id.job_id.name", tracking=True)
    nationality = fields.Char(related="employee_id.country_id.name", tracking=True)
    identification_number = fields.Char(related="employee_id.identification_id", tracking=True)
    location = fields.Char(related="employee_id.location.name", tracking=True)
    hire_date = fields.Date(tracking=True, related='employee_id.contract_id.date_start')
    last_working_date = fields.Date(tracking=True, compute='get_last_working_date', store=True)
    last_return_date = fields.Date(tracking=True, compute='get_last_return_date', store=True)
    # service_period = fields.Date(tracking=True)
    service_period_2 = fields.Float(tracking=True, related='employee_id.total_service_years')
    entitlement_of_annual_leave = fields.Char(tracking=True)
    balance_leave_2 = fields.Float(tracking=True, related='employee_id.net_days')
    leave_balance_amount = fields.Float(tracking=True, related='employee_id.amount_of_net_days')
    leave_start_date = fields.Date(tracking=True)
    leave_return_date = fields.Date(tracking=True)
    leave_duration = fields.Integer(tracking=True, compute='_compute_leave_duration')
    unpaid_leave_days = fields.Integer(tracking=True, compute="get_unpaid_leave_days")

    departure_reason = fields.Many2one('hr.departure.reason', tracking=True)
    reason_of_the_end_of_contract = fields.Char(tracking=True)
    start_notice_period = fields.Date(tracking=True)
    end_notice_period = fields.Date(tracking=True)
    additional_information = fields.Char(tracking=True)
    departure_date = fields.Date(tracking=True)
    duration = fields.Integer(tracking=True)

    time_off_count = fields.Integer(compute='get_time_off_count')
    resignation_request_count = fields.Integer(compute='get_resignation_request_count')
    payslips_count = fields.Integer(compute='get_payslips_count')
    equipment_count = fields.Integer()
    salary_advance_count = fields.Integer(compute='get_salary_advance_count')
    employee_clearance_count = fields.Integer(compute='get_employee_clearance_count')
    flight_tickets_count = fields.Integer(compute='get_flight_tickets_count')

    @api.depends('leave_start_date', 'leave_return_date')
    def _compute_leave_duration(self):
        for rec in self:
            if rec.leave_start_date and rec.leave_return_date:
                start_date = fields.Date.from_string(rec.leave_start_date)
                return_date = fields.Date.from_string(rec.leave_return_date)
                rec.leave_duration = (return_date - start_date).days + 1
            else:
                rec.leave_duration = 0

    @api.depends('leave_duration', 'leave_balance_amount')
    def get_unpaid_leave_days(self):
        for rec in self:
            if rec.leave_duration and rec.leave_balance_amount:
                rec.unpaid_leave_days = rec.leave_duration - rec.leave_balance_amount
                if rec.unpaid_leave_days < 0:
                    rec.unpaid_leave_days = 0
            else:
                rec.unpaid_leave_days = 0


    def action_cancel(self):
        for rec in self:
            if rec.annual_leave_id:
                if rec.annual_leave_id.state not in ('confirm', 'refuse', 'cancel'):
                    raise ValidationError(_("You can't cancel this clearance ,The requested leave has been approved"))
                else:
                    if rec.annual_leave_id.state in ('confirm', 'cancel',):
                        rec.annual_leave_id.sudo().unlink()
                        rec.state = 'cancel'
                    elif rec.annual_leave_id.state == 'refuse':
                        rec.annual_leave_id.sudo().action_reset_confirm()
                        rec.annual_leave_id.sudo().unlink()
                        rec.state = 'cancel'
                    else:
                        rec.annual_leave_id.sudo()._action_user_cancel(reason="Clearance Cancel")
                        rec.annual_leave_id.sudo().unlink()
                        rec.state = 'cancel'
            if rec.resignation_request_id:
                if rec.resignation_request_id.state != 'draft':
                    raise ValidationError(
                        _("You can't cancel this clearance ,The requested resignation has been confirmed"))
                else:
                    rec.resignation_request_id.sudo().unlink()
                    rec.state = 'cancel'
            if not rec.annual_leave_id and not rec.resignation_request_id:
                rec.state = 'cancel'

    def action_submit(self):
        for rec in self:
            rec.state = 'finance_approval'

    def action_finance_approve(self):
        for rec in self:
            rec.state = 'it_approval'

    def action_it_approval(self):
        for rec in self:
            rec.state = 'sales_approval'

    def action_sales_approval(self):
        for rec in self:
            rec.state = 'inventory_approval'

    def action_inventory_approval(self):
        for rec in self:
            rec.state = 'hr_approval'



    def action_hr_approval(self):
        for rec in self:
            if rec.application_type == 'annual_leave':
                holiday_status_id = None
                holiday_status_all = self.env['hr.leave.type'].search([])
                for holiday_status in holiday_status_all:
                    if holiday_status.name.lower() == 'annual leave':
                        holiday_status_id = holiday_status.id
                        break
                if holiday_status_id:
                    leave_vals = {
                        'name': 'Annual Leave for %s' % rec.employee_id.name,
                        'employee_id': rec.employee_id.id,
                        'request_date_from': rec.leave_start_date,
                        'request_date_to': rec.leave_return_date,
                        'holiday_status_id': holiday_status_id,
                    }
                    rec.annual_leave_id = self.env['hr.leave'].create(leave_vals)
                    rec.state = 'approved'
            if rec.application_type == 'end_of_service':
                resignation_vals = {
                    'employee_id': rec.employee_id.id,
                    'date': rec.departure_date,
                    'hr_departure_id': rec.departure_reason.id,
                }
                rec.resignation_request_id = self.env['resignation.request'].create(resignation_vals)
                rec.state = 'approved'


    def action_set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.depends('employee_id')
    def get_last_return_date(self):
        for rec in self:
            if rec.employee_id.return_vacation_ids:
                rec.last_return_date = rec.employee_id.return_vacation_ids[-1].return_date
            else:
                rec.last_return_date = None

    @api.depends('employee_id')
    def get_last_working_date(self):
        for rec in self:
            if rec.employee_id.return_vacation_ids:
                rec.last_working_date = rec.employee_id.return_vacation_ids[-1].actual_return_date
            else:
                rec.last_working_date = None

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('clearance') or '/'
        return super(Clearance, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state not in  ('draft', 'cancel'):
                record.action_cancel()
                record.action_set_to_draft()
            if record.state == 'cancel':
                record.action_set_to_draft()
        return super().unlink()

    @api.depends('employee_id')
    def get_time_off_count(self):
        for rec in self:
            hr_leave = self.env['hr.leave'].search_count([
                ('employee_id', '=', rec.employee_id.id)
            ])
            rec.time_off_count = hr_leave

    @api.depends('employee_id')
    def get_resignation_request_count(self):
        for rec in self:
            resignation_request = self.env['resignation.request'].search_count([
                ('employee_id', '=', rec.employee_id.id)
            ])
            rec.resignation_request_count = resignation_request

    @api.depends('employee_id')
    def get_payslips_count(self):
        for rec in self:
            hr_payslip = self.env['hr.payslip'].search_count([
                ('employee_id', '=', rec.employee_id.id)
            ])
            rec.payslips_count = hr_payslip

    # @api.depends('employee_id')
    # def get_salary_advance_count(self):
    #     for rec in self:
    #         salary_advance = self.env['salary.advance'].search_count([
    #             ('employee_id', '=', rec.employee_id.id)
    #         ])
    #         rec.salary_advance_count = salary_advance



    @api.depends('employee_id')
    def get_employee_clearance_count(self):
        for rec in self:
            employee_clearance = self.env['employee.clearance'].search_count([
                ('employee_id', '=', rec.employee_id.id)
            ])
            rec.employee_clearance_count = employee_clearance

    @api.depends('employee_id')
    def get_flight_tickets_count(self):
        for rec in self:
            flight_tickets = self.env['flight.tickets'].search_count([
                ('employee_id', '=', rec.employee_id.id)
            ])
            rec.flight_tickets_count = flight_tickets

    def action_view_flight_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Flight Ticket',
            'view_mode': 'list,form',
            'res_model': 'flight.tickets',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    def action_view_time_off(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Time Off',
            'view_mode': 'list,form',
            'res_model': 'hr.leave',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    def action_view_resignation_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resignation Request',
            'view_mode': 'list,form',
            'res_model': 'resignation.request',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    def action_view_payslip(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payslips',
            'view_mode': 'list,form',
            'res_model': 'hr.payslip',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    def action_view_equipment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equipment',
            'view_mode': 'list,form',
            'res_model': 'equipment',
            # 'domain': [('employee_id', '=', self.employee_id.id)],
            # 'context': {'default_employee_id': self.id},
        }
    #
    # def action_view_loans(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Loans',
    #         'view_mode': 'tree,form',
    #         'res_model': 'salary.advance',
    #         'domain': [('employee_id', '=', self.employee_id.id)],
    #         'context': {'default_employee_id': self.employee_id.id},
    #     }

    def action_view_employee_clearance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Clearance',
            'view_mode': 'list,form',
            'res_model': 'employee.clearance',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }


class EmployeeClearance(models.Model):
    _name = 'employee.clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'EmployeeClearance'

    name = fields.Char(tracking=True)
    employee_id = fields.Many2one('hr.employee', tracking=True)
    date_of_application = fields.Date(tracking=True)
    employee_clearance_ids = fields.One2many('employee.clearance.line', 'employee_clearance_id')


class EmployeeClearanceLine(models.Model):
    _name = 'employee.clearance.line'

    operating_unit = fields.Char()
    actions_required = fields.Char()
    actions_confirmation = fields.Char()
    carried_out_by = fields.Char()
    Date = fields.Date()
    notes = fields.Char()
    employee_clearance_id = fields.Many2one('employee.clearance')
