from odoo import api, fields, models


class Equipment(models.Model):
    _name = 'equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Equipment Name', tracking=True)
    used_by = fields.Selection([('employee', 'Employee'), ('department', 'Department'), ('location', 'Location')],
                               tracking=True)
    employee = fields.Many2one('hr.employee', readonly=True, tracking=True)
    department = fields.Many2one('hr.department', tracking=True)
    location = fields.Many2one('location', tracking=True)
    purchase_date = fields.Date(tracking=True)
    scrap_date = fields.Date(tracking=True)
    transfer_of_responsibility_records = fields.Char(tracking=True)
    supplier = fields.Many2one('res.partner', tracking=True)
    model = fields.Char(tracking=True)
    serial_number = fields.Integer(tracking=True)
    cost = fields.Float(tracking=True)
    warranty_expiration_date = fields.Date(tracking=True)
    equipment_id = fields.Many2one('hr.employee', string="Name", tracking=True)


class JoiningType(models.Model):
    _name = 'joining.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Joining Type'

    name = fields.Char(string="Type", tracking=True)


class ReasonEndContract(models.Model):
    _name = 'reason.end.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Reason End Of Contract'

    name = fields.Char(string="Reason End Of Contract", tracking=True)


class EmployeeContribution(models.Model):
    _name = 'employee.contribution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Contribution'

    name = fields.Char(string="Employee Contribution", tracking=True)


class EmployeeFamilyMember(models.Model):
    _name = 'employee.family.member'
    _description = 'Employee family Member'

    relation_id = fields.Many2one('hr.employee', string='Employee')
    name = fields.Char(string="Name")
    relational = fields.Selection(string='Relational',
                                  selection=[('wife', 'Wife'),
                                             ('husband', 'Husband'),
                                             ('doughtier', 'Doughtier'),
                                             ('son', 'Son'),
                                             ],
                                  required=False, )
    gender_member = fields.Selection(string='Gender',
                                     selection=[('male', 'Male'),
                                                ('female', 'Female'), ],
                                     required=False, )
    member_date_of_birth = fields.Date(string='Date Of Birth', required=False)
    member_age = fields.Integer(string='Age', required=False)
    include_in_ticket = fields.Boolean(string='Include In Ticket', required=False)
    member_medical_insurance = fields.Char(string='Medical Insurance', required=False)
    id_number = fields.Integer(string='Id Number', required=False)
    passport_number = fields.Char(string='Passport Number', required=False)



class Documents(models.Model):
    _name = 'document.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    state = fields.Selection([('running', 'Running'), ('neer_expiry', 'Neer Expiry'), ('expired', 'Expired')])
    document_id = fields.Many2one('hr.employee', string='Employee', traking=True)
    document_stages = fields.Selection(string='Document Stages',
                                       selection=[('running', 'Running'),
                                                  ('near_expiry', 'Near Expiry'),
                                                  ('expired', 'expired'),
                                                  ], traking=True,
                                       required=False)
    document_type_2 = fields.Many2one('document.type.custom', string='Document Type', required=False, traking=True)
    document_issue_date = fields.Date(string='Document Issue Date', required=False, traking=True)
    document_expiry_date = fields.Date(string='Document Expiry Date', required=False, traking=True)
    document_expiry_date_alart = fields.Integer(string='Document Expiry Date Alart', required=False, traking=True)
    employee_id = fields.Many2one('hr.employee', string='Related Employee', required=False, traking=True)
    attachment = fields.Binary(string="Attachment", traking=True)
    coustdian = fields.Many2one('res.company', string='Coustdian', required=False, traking=True)

    @api.onchange('document_type_2', 'document_expiry_date')
    def get_name(self):
        for rec in self:
            if rec.document_type_2 and rec.document_expiry_date:
                rec.name = f"{rec.document_type_2.name} ({rec.document_expiry_date.strftime('%Y-%m-%d')})"
            else:
                rec.name = ''


class DocumentTypeCustom(models.Model):
    _name = 'document.type.custom'

    name = fields.Char()


class AllowanceTags(models.Model):
    _name = 'allowance.tags'

    name = fields.Char()


class Religion(models.Model):
    _name = 'religion'
    _description = 'Religion'

    name = fields.Char()


class Followers(models.Model):
    _name = 'followers'
    _description = 'Followers'

    followers_id = fields.Many2one(comodel_name="hr.employee")
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection(string="Gender", selection=[('male', 'Male'), ('female', 'Female'), ], required=True)
    birthday = fields.Date(string="Birthday")
    identification_id = fields.Char(string="Identification No")

