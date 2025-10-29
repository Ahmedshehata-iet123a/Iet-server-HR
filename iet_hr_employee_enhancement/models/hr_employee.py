from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.osv import expression


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    arabic_name = fields.Char(string='Arabic Name', required=False)
    badge_number = fields.Char(string='Badge Number', required=False)
    employee_type_2 = fields.Selection(string='Employee Type',
                                       selection=[('local', 'Local'),
                                                  ('remote', 'Remote'), ],
                                       required=False, )
    occupation = fields.Many2one('hr.job', string='Occupation', required=False)
    joining_type_id = fields.Many2one('joining.type', string='Joining Type', required=False)
    last_start_work_date = fields.Date(string='Last Start Work Date', required=False)
    insurance_policy_number = fields.Char(required=False)
    insurance_medical = fields.Char(string='Medical Insurance Scheme', required=False)
    insurance_end_date = fields.Date(string='Insurance Termination Date', required=False)
    shoe_size = fields.Char()
    shirt_size = fields.Char()
    pant_size = fields.Char()
    departure_reason = fields.Char(string='Departure Reason', required=False)
    reason_end_contract_id = fields.Many2one('reason.end.contract', string='Reason End Contract', required=False)
    start_notice_date = fields.Date(string='Start Notice Date', required=False)
    end_notice_date = fields.Date(string='End Notice Date', required=False)
    addition_information = fields.Char(string='Addition Information', required=False)
    bank_iban_number = fields.Char(string='Bank Iban Number', required=False)
    bank_name = fields.Char(related="bank_account_id.bank_id.name", readonly=True, string="Bank Name", store=True, )
    bank_code = fields.Char(related="bank_account_id.bank_id.bic", readonly=True, string="Bank Code", store=True, )
    employee_age = fields.Integer(string='Employee Age', compute='_compute_age')
    custom_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], groups="hr.group_hr_user", tracking=True, string='Gender')

    blood_type = fields.Selection(
        [('A+', 'A+'), (' A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'),
         ('AB-', 'AB-'), ], string='Blood Type')
    gosi_number = fields.Char(string='Gosi Number', required=False)
    gosi_registration_date = fields.Date(string='Gosi Registration Date', required=False)
    gosi_salary = fields.Integer(string='Gosi Salary', required=False)
    Gosi_total_salary = fields.Integer(string='Gosi Total Salary', required=False)
    employee_contribution_coverage_id = fields.Many2one('employee.contribution',
                                                        string='Employee contribution Coverage', required=False)
    employee_contribution_amount = fields.Integer(string='Employee Contribution Amount', required=False)
    employee_family_information_relation = fields.One2many('employee.family.member', 'relation_id', string="Data")
    location_transfer_relation = fields.One2many('location.transfer', 'relation_id3', string="Data")
    days_unpaid_time_off = fields.Integer(string='Days Unpaid Time Off', required=False)
    service_period = fields.Date(string='Service Period', required=False)

    current_year = fields.Integer(string='Current Year', default=datetime.now().year)
    document_ids = fields.One2many('document.line', 'document_id')
    location = fields.Many2one('location')
    employee_number = fields.Char("Employee Number", default=lambda self: _('00000'),
       copy=False, tracking=True)
    location_transfer_count = fields.Integer(
        compute='_compute_location_transfer_count', string='Location Transfers')
    employee_family_information_relation_count = fields.Integer(
        compute='_compute_employee_family_information_relation_count', string='Family Information')
    document_ids_count = fields.Integer(
        compute='_compute_document_ids_count', string='Documents')
    equipment_ids = fields.One2many('equipment', 'equipment_id')
    equipment_ids_count = fields.Integer(
        compute='_compute_equipment_ids_count', string='Documents')
    insurance_info_config = fields.Boolean(compute='get_employee_config',)
    work_uniform_measurement_config = fields.Boolean(compute='get_employee_config',)

    attachment_ids = fields.Many2many('ir.attachment', required=False)

    end_date_identification = fields.Date(string="identification End Date")
    end_date_passport = fields.Date(string="Passport End Date")
    attachment_identification = fields.Binary(string="Identification Attachment", attachment=True)
    attachment_passport = fields.Binary(string="Passport Attachment", attachment=True)
    followers_ids = fields.One2many(comodel_name="followers", inverse_name="followers_id")
    border_num = fields.Char(string="Border Number")
    date_of_entry = fields.Date(string="Date of entry")

    custom_employee_pin_number = fields.Char(string="Employee Number", readonly=False)

    employee_custom_analytic_id = fields.Many2one('employee.analytic.report',
                                                  compute='_compute_employee_custom_analytic_id',
                                                  store=True,
                                                  string="Employee Analytic")

    _sql_constraints = [
        ('unique_employee_number', 'unique (employee_number)', _('Employee Number already exists!')),
        ('unique_gosi_number', 'unique (gosi_number)', _('Employee GOSI Number already exists!')),
        ('unique_identification_id', 'unique (identification_id)', _('Employee Identification already exists!')),
        ('unique_bank_iban_number', 'unique (bank_iban_number)', _('Employee Bank Iban Number already exists!')),
        ('unique_work_email', 'unique (work_email)', _('Employee Work Email already exists!')),
        # ('unique_work_phone', 'unique (work_phone)', _('Employee Work Phone already exists!')),
    ]

    @api.depends('name')
    def _compute_employee_custom_analytic_id(self):
        print("_compute_employee_custom_analytic_id")
        for rec in self:
            if rec.name:
                custom_analytic_id = self.env['employee.analytic.report'].search([('employee_id', '=', rec.id)])
                if custom_analytic_id:
                    rec.employee_custom_analytic_id = custom_analytic_id[0].id
                else:
                    rec.employee_custom_analytic_id = False

    def get_employee_config(self):
        for employee in self:
            config = self.env['ir.config_parameter'].sudo()
            employee.insurance_info_config = config.get_param('iet_hr_employee_enhancement.hr_employee_insurance_information', )
            employee.work_uniform_measurement_config = config.get_param(
                'iet_hr_employee_enhancement.hr_employee_work_uniform_measurement', )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_number', '00000') == '00000':
                vals['employee_number'] = (self.env['ir.sequence'].
                                  next_by_code('employee_number.seq.code'))
        return super(HrEmployeeInherit, self).create(vals_list)


    # @api.model
    # def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
    #     domain = domain or []
    #     if operator != 'ilike' or (name or '').strip():
    #         name_domain = ['|', ('name', 'ilike', name), ('employee_number', 'ilike', name)]
    #         domain = expression.AND([name_domain, domain])
    #     return self._search(domain, limit=limit, order=order)

    @api.model
    def _search_display_name(self, operator, value):
        domain = []
        if operator != 'ilike' or (value or '').strip():
            criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
            name_domain = criteria_operator + [
                ('name', operator, value),
                ('employee_number', operator, value)
            ]
            domain = expression.AND([name_domain, domain])
        return domain

    def action_set_employee_number_sequence_code(self):
        for record in self:
            if not record.employee_number:
                code = (self.env['ir.sequence'].
                                  next_by_code('employee_number.seq.code'))
                record.write({'employee_number': code})


    @api.constrains('bank_iban_number')
    def _check_bank_iban_number(self):
        for record in self:
            if record.bank_iban_number and len(record.bank_iban_number) != 24:
                raise ValidationError(_("The bank IBAN number must contain 24 characters."))


    @api.constrains('identification_id')
    def _check_identification_id(self):
        for record in self:
            if record.identification_id and len(record.identification_id) != 10:
                raise ValidationError("The Employee Identification Number must contain 10 characters.")


    @api.depends('location_transfer_relation')
    def _compute_location_transfer_count(self):
        for employee in self:
            location_transfers = self.env['location.transfer'].search_count([
                ('relation_id3', '=', employee.id)
            ])
            employee.location_transfer_count = location_transfers

    def action_view_location_transfers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Location Transfers',
            'view_mode': 'list,form',
            'res_model': 'location.transfer',
            'domain': [('relation_id3', '=', self.id)],
            'context': {'default_relation_id3': self.id},
        }

    @api.depends('employee_family_information_relation')
    def _compute_employee_family_information_relation_count(self):
        for employee in self:
            family_information = self.env['employee.family.member'].search_count([
                ('relation_id', '=', employee.id)
            ])
            employee.employee_family_information_relation_count = family_information

    def action_view_family_information(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Family Information',
            'view_mode': 'list,form',
            'res_model': 'employee.family.member',
            'domain': [('relation_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    @api.depends('document_ids')
    def _compute_document_ids_count(self):
        for employee in self:
            documents = self.env['document.line'].search_count([
                ('document_id', '=', employee.id)
            ])
            employee.document_ids_count = documents

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Documents',
            'view_mode': 'list,form',
            'res_model': 'document.line',
            'domain': [('document_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    @api.depends('equipment_ids')
    def _compute_equipment_ids_count(self):
        for employee in self:
            equipments = self.env['equipment'].search_count([
                ('employee', '=', self.id)
            ])
            employee.equipment_ids_count = equipments

    def action_view_equipment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equipments',
            'view_mode': 'list,form',
            'res_model': 'equipment',
            'domain': [('employee', '=', self.id)],  # assuming 'employee' field links to hr.employee
            'context': {'default_employee': self.id},
        }

    @api.depends('birthday', 'current_year')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                if isinstance(record.birthday, date):  # Check if birthday is already a date object
                    birth_year = record.birthday.year
                else:
                    birth_year = datetime.strptime(str(record.birthday), '%Y-%m-%d').year
                record.employee_age = record.current_year - birth_year
            else:
                record.employee_age = 0

    def print_report(self):
        pass

    @api.model
    def notify_employee_date(self):
        today = date.today()
        one_month_come = today + relativedelta(months=1)
        three_month_come = today + relativedelta(months=3)
        print(one_month_come)
        print(three_month_come)
        employees = self.search(
            ["|", ('end_date_identification', '=', one_month_come), ('contract_id.date_end', '=', three_month_come)])
        for employee in employees:
            msgs = []
            if employee.end_date_identification == one_month_come:
                msgs.append(_('Mr./Ms.') + str(employee.name) + _(
                    'has only 6 month left until his identification number expires.'))
            if employee.contract_id.date_end == three_month_come:
                msgs.append(_('Mr./Ms.') + str(employee.name) + _('has only 3 month left until his contract expires.'))
            if msgs:
                for msg_body in msgs:
                    message = self.env['mail.message'].create({
                        'author_id': self.id,
                        'model': self._name,  # Use the model name directly
                        'res_id': employee.id,
                        'date': datetime.now(),
                        'subtype_id': self.env.ref('mail.mt_comment').id,
                        'body': msg_body
                    })
                    # for user in self.env['res.users'].search([('id', 'in', self.env.ref(
                    #         'iet_employee_notifications.group_employee_notification_manager').users.ids)]):
                    notification_managers = self.env.ref(
                        'iet_hr_employee_enhancement.group_employee_notification_manager').users
                    for user in notification_managers:
                        # Create a mail.notification record
                        self.env['mail.notification'].create({
                            'author_id': message.author_id.id,
                            'mail_message_id': message.id,
                            'notification_type': 'inbox',
                            'res_partner_id': user.partner_id.id,
                            'notification_status': 'sent',  # Optional, but useful to indicate status
                        })
