from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    probation_period = fields.Integer(string='Probation Period', required=False)
    probation_end_date = fields.Date(string='Probation End Date', required=False, compute='_compute_probation_end_date')
    # food_allowance = fields.Integer(string='Food Allowance', required=False)
    contract_status = fields.Selection(string='Contract_status',
                                       selection=[('family', 'Family'),
                                                  ('single', 'Single'), ],
                                       required=False)
    medical_insurance = fields.Boolean(string='Medical Insurance', required=False)
    medical_insurance_members = fields.Integer("Medical Insurance Members")
    medical_insurance_amount = fields.Monetary("Medical Insurance Value")
    company_car = fields.Boolean(string='Company Car', required=False)
    car_number = fields.Char(string='Car Number', required=False)
    accommodation = fields.Boolean(string='Accommodation', required=False)
    accommodation_cost = fields.Monetary("Accommodation Cost")
    air_ticket = fields.Boolean(string='Air Ticket', required=False)
    air_ticket_cost = fields.Monetary("Ticket Cost")
    number_of_tickets = fields.Integer()
    qiwa_contract_create = fields.Boolean(string='Qiwa Contract Create', required=False)
    qiwa_contract_approved = fields.Boolean(string='Qiwa Contract Approved By Employee', required=False)
    gosi_salary_information_update = fields.Boolean(string='GOSI Salary Information Updated', required=False)
    number_of_unpaid_days = fields.Integer(string='Number Of Unpaid Days', required=False)
    number_of_sick_leaves = fields.Integer(string='Number Of Sick Leaves', required=False)
    # number_of_absent_days = fields.Integer(string='Number Of Absent Days', required=False)
    is_emp_active = fields.Boolean(related="employee_id.active")
    is_cheked = fields.Boolean(string='Expired')
    automatic_contract_renewal = fields.Selection([('yes', 'Yes'), ('no', 'No')], tracking=True)
    occupation = fields.Many2one('hr.job', related='employee_id.occupation')
    num_of_years_for_contract = fields.Selection(string="", selection=[('one', 'One Year'), ('two', 'Two Years'), ],
                                                 required=False, default='two', tracking=True)
    contract_period = fields.Integer(string="Contract Period", default=1, tracking=True,
                                     compute='_compute_contract_period', store=True)
    notice_period = fields.Integer(string='Notice Period', tracking=True)
    date_end = fields.Date('End Date', tracking=True, compute='_compute_date_end', store=True,
                           help="End date of the contract (if it's a fixed-term contract).")
    total_salary = fields.Monetary(string='Total Salary', compute='_compute_total_salary', store=True)

    @api.depends('wage', )
    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = rec.wage or 0.0

    @api.depends('probation_period', 'date_start')
    def _compute_probation_end_date(self):
        for rec in self:
            if rec.probation_period:
                rec.probation_end_date = rec.date_start + timedelta(days=rec.probation_period)

            else:
                rec.probation_end_date = False

    def get_number_of_leave_days(self):
        for rec in self:
            unpaid_leaves = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.work_entry_type_id.name', 'like', 'Unpaid'), ])
            rec.number_of_unpaid_days = len(unpaid_leaves)

            sick_leaves = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.work_entry_type_id.name', 'like', 'Sick Time Off'), ])
            rec.number_of_sick_leaves = len(sick_leaves)


    @api.onchange('state')
    def onchange_state_for_expired_contract(self):
        print("onchange_state_for_expired_contract")
        for rec in self:
            if rec.state == 'close':
                rec.is_cheked = True

    @api.depends('num_of_years_for_contract')
    def _compute_contract_period(self):
        for rec in self:
            if rec.num_of_years_for_contract == 'one':
                rec.contract_period = 1
            elif rec.num_of_years_for_contract == 'two':
                rec.contract_period = 2
            else:
                rec.contract_period = 0

    @api.depends('date_start', 'contract_period')
    def _compute_date_end(self):
        for rec in self:
            if rec.date_start:
                if rec.contract_period and rec.contract_period >= 0:
                    result_2 = rec.date_start + relativedelta(years=rec.contract_period)
                    rec.date_end = result_2 + timedelta(days=-1)
                else:
                    rec.date_end = False

    @api.model
    def action_is_cheked(self):
        print('action_is_cheked')
        current_date = datetime.today()
        asd_date = '2011-01-01'
        all_contracts_not_closed = self.env['hr.contract'].search(
            [('automatic_contract_renewal', '=', 'no'), ('is_emp_active', '=', True)])
        if all_contracts_not_closed:
            for c in all_contracts_not_closed:
                if c.state != 'close' and c.state != 'cancel':
                    c.state = 'close'
        all_contracts = self.env['hr.contract'].search([('date_end', '<=', current_date.date()),
                                                        ('date_start', '>=', asd_date),
                                                        ('state', '!=', 'close'),
                                                        ('automatic_contract_renewal', '=', 'yes')])
        if all_contracts:
            for rec in all_contracts:
                current_date = datetime.today()
                if rec.employee_id.active == True:
                    if rec.automatic_contract_renewal == 'yes' and rec.date_end <= current_date.date():
                        date1 = rec.date_start
                        date2 = rec.date_end
                        rec.state = 'close'

                        date_start = date2 + relativedelta(days=1)
                        date_end = date2 + relativedelta(years=rec.contract_period)

                        new_contract = rec.copy({
                            'state': 'draft',
                            'date_start': date_start,
                            'date_end': date_end,
                            'number_of_unpaid_days': 0,
                            'number_of_sick_leaves': 0,
                        })
                        for line in rec.contract_history_line_ids:
                            line.copy({
                                'contract_id': new_contract.id,
                            })

                        new_contract.state = 'open'

