from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class RequestChangeSalaryAccount(models.Model):
    _name = 'request.change.salary.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(default=lambda self: _('New'),
                           copy=False, readonly=True, tracking=True, string='Request Number')
    name = fields.Char(string='Request Name', default='Request to change salary account')
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True,required=True)
    employee_code = fields.Char(string='Employee Number', related='employee_id.employee_number', readonly=True,
                                store=True, tracking=True)
    request_date = fields.Date(string='Request Date', tracking=True)
    current_request_no = fields.Many2one('res.partner.bank', string='Current Bank Account',
                                         related='employee_id.bank_account_id',tracking=True, store=True)
    old_request_no = fields.Many2one('res.partner.bank', string='Old Bank Account', readonly=True)
    new_request_no = fields.Many2one('res.partner.bank', string='New Bank Account', tracking=True,)
    bank_iban_number = fields.Char(string='Bank Iban Number', related="employee_id.bank_iban_number")
    bank_name = fields.Char(related="employee_id.bank_account_id.bank_id.name", readonly=True, string="Bank Name" )
    bank_code = fields.Char(related="employee_id.bank_account_id.bank_id.bic", readonly=True, string="Bank Code" )

    # new_request_no = fields.Char(string='New Account Number', tracking=True)
    evacuation_bank = fields.Binary(string='Evacuation Bank', tracking=True)
    reason = fields.Char(string='Reason', tracking=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('hr_approval', 'To HR Approval'),
        ('financial_management_approval', 'Financial Management Approval'),
        ('done', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancel'),
    ], default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = (self.env['ir.sequence'].
                                    next_by_code('request.change.salary.account.seq.code'))
        return super().create(vals_list)

    def _send_activity(self, model_id, users, summary, note):
        for user in users:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': summary,
                'note': note,
                'res_id': model_id.id,
                'res_model_id': self.env['ir.model'].search(
                    [('model', '=', 'request.change.salary.account')]).id,
                'user_id': user.id,
            })

    def action_submit(self):
        for rec in self:
            rec.state = 'hr_approval'
            users = self.env['res.users'].search(
                [('groups_id', 'in', (self.env.ref('iet_hr_employee_enhancement.group_hr_officer').id,
                                      self.env.ref('iet_hr_employee_enhancement.group_hr_manager').id))])
            summary = 'Request Approve'
            note = 'You Should Approve This Request'
            model_id = self.env['request.change.salary.account'].search([('id', '=', rec.id)])
            self._send_activity(model_id, users, summary, note)

    def action_hr_approval(self):
        for rec in self:
            rec.state = 'financial_management_approval'

    def action_financial_manager_approval(self):
        for rec in self:
            old_request_no = rec.employee_id.bank_account_id
            if rec.new_request_no:
                rec.employee_id.bank_account_id = rec.new_request_no
            rec.old_request_no = old_request_no
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_hr_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
