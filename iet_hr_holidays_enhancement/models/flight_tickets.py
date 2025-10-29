from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FlightTickets(models.Model):
    _name = 'flight.tickets'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    # name = fields.Many2one('hr.employee', string='Employee')
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('refuse', 'Refused')],
                             default='draft')
    booked_by = fields.Selection(
        [('company', 'Company'), ('employee', 'Employee'), ('recruiting_agency', 'Recruiting Agency')], tracking=True)
    flight_for = fields.Selection(
        [('employee', 'Employee'), ('employee_and_dependents', 'Employee And Dependents'),
         ('dependents', 'Dependents')], tracking=True)
    number_of_tickets = fields.Integer(tracking=True)
    flight_date = fields.Date(tracking=True)
    trip_type = fields.Selection(
        [('round', 'Round'), ('one_way', 'One Way')], tracking=True)
    initial_flight_type = fields.Selection(
        [('outbound', 'Outbound'), ('inbound', 'Inbound')], tracking=True)
    departure_airport = fields.Char(tracking=True)
    Arrival_airport = fields.Char(tracking=True)
    flight_ticket_cost = fields.Float(tracking=True)
    employees_contribution_to_the_flight_ticket = fields.Float(tracking=True)
    visa_period = fields.Integer(string='Visa Period (Days)', tracking=True)
    number_of_tickets_contract = fields.Integer(compute='get_number_of_tickets_contract', store=True)
    available_tickets = fields.Integer(compute='get_available_tickets', store=True)

    def action_submit(self):
        self.state = 'submit'

    def action_approve(self):
        self.state = 'approve'

    def action_refuse(self):
        self.state = 'refuse'

    def action_draft(self):
        self.state = 'draft'

    @api.depends('number_of_tickets', 'number_of_tickets_contract')
    def get_available_tickets(self):
        for rec in self:
            if rec.number_of_tickets_contract and rec.number_of_tickets:
                rec.available_tickets = rec.number_of_tickets_contract - rec.number_of_tickets
            else:
                rec.available_tickets = 0

    @api.depends('employee_id')
    def get_number_of_tickets_contract(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.contract_id:
                rec.number_of_tickets_contract = rec.employee_id.contract_id.number_of_tickets
            else:
                rec.number_of_tickets_contract = 0

    @api.model
    def create(self, vals):
        # Constraint check
        # if 'number_of_tickets' in vals and 'employee_id' in vals:
        #     print(1)
        #     employee = self.env['hr.employee'].browse(vals['employee_id']) or False
        #     if employee and employee.contract_id and employee.contract_id.number_of_tickets:
        #         print(3)
        #         if vals['number_of_tickets'] > employee.contract_id.number_of_tickets:
        #             print(4)
        #             raise ValidationError(
        #                 "The Number Of Tickets Must Be Less Than Or Equal To The Number Of Tickets In Contract")

        # Sequence generation
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('flight.tickets') or '/'

        return super(FlightTickets, self).create(vals)

    def write(self, vals):
        for record in self:
            number_of_tickets = vals.get('number_of_tickets', record.number_of_tickets)
            number_of_tickets_contract = vals.get('number_of_tickets_contract', record.number_of_tickets_contract)

            if number_of_tickets > number_of_tickets_contract:
                raise ValidationError(
                    "The Number Of Tickets Must Be Less Than Or Equal To The Number Of Tickets In Contract")

        return super(FlightTickets, self).write(vals)
