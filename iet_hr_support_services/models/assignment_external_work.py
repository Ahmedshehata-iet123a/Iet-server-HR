from odoo import fields, api, models,_
from odoo.exceptions import ValidationError


class AssignmentExternalWork(models.Model):
    _name = 'assignment.external.work'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(default=lambda self: _('New'),
                           copy=False, readonly=True, tracking=True, string='Request Number')
    name = fields.Char(string='Request Name',default='Assignment of an external work.')
    employee_id = fields.Many2one('hr.employee', string='Employee',required=True, tracking=True)
    employee_code = fields.Char(string='Employee Number',related='employee_id.employee_number',readonly=True,store=True,tracking=True)
    request_date = fields.Date(string='Request Date',tracking=True)
    new_request_no = fields.Char(string='New Request Number',tracking=True)
    evacuation_bank = fields.Binary(string='Evacuation Bank',tracking=True)
    reason = fields.Char(string='Reason',tracking=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('hr_approval','HR Approval'),
        ('financial_management_approval','Financial Management Approval'),
        ('done','done'),
        ('reject','Reject'),
        ('cancel','Cancel'),
    ],default='draft',tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = (self.env['ir.sequence'].
                                    next_by_code('assignment.external.work.seq.code'))
        return super().create(vals_list)

    def _send_activity(self, model_id, users, summary, note):
        for user in users:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': summary,
                'note': note,
                'res_id': model_id.id,
                'res_model_id': self.env['ir.model'].search(
                [('model', '=', 'assignment.external.work')]).id,
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
            model_id = self.env['assignment.external.work'].search([('id', '=', rec.id)])
            self._send_activity(model_id, users, summary, note)

    def action_hr_approval(self):
        for rec in self:
            rec.state = 'financial_management_approval'

    def action_financial_manager_approval(self):
            for rec in self:
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
