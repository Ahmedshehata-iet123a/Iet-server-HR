from odoo import fields, api, models,_
from odoo.exceptions import ValidationError


class RequestMaintenanceDevicesPrinters(models.Model):
    _name = 'request.maintenance.devices.printers'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(default=lambda self: _('New'),
                           copy=False, readonly=True, tracking=True, string='Request Number')
    name = fields.Char(string='Request Name' ,default='Request for maintenance of devices and printers')
    employee_id = fields.Many2one('hr.employee', string='Employee',tracking=True,required=True)
    employee_code = fields.Char(string='Employee Number',related='employee_id.employee_number',readonly=True,store=True,tracking=True)
    request_date = fields.Date(string='Request Date',tracking=True)
    reason = fields.Char(string='Reason',tracking=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('manager_approval', 'To Direct approval'),
        ('department_manager_approval', 'To Department Approval'),
        ('hr_approval', 'To HR Approval'),
        ('it_approval', 'To IT Approval'),
        ('done', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancel'),
    ], default='draft', tracking=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = (self.env['ir.sequence'].
                                    next_by_code('request.maintenance.devices.printers.seq.code'))
        return super().create(vals_list)

    def _send_activity(self, model_id, users, summary, note):
        for user in users:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': summary,
                'note': note,
                'res_id': model_id.id,
                'res_model_id': self.env['ir.model'].search(
                [('model', '=', 'request.maintenance.devices.printers')]).id,
                'user_id': user.id,
            })

    def action_submit(self):
        for rec in self:
            rec.state = 'manager_approval'
            users = rec.employee_id.parent_id.user_id
            summary = 'Request Approve'
            note = 'You Should Approve This Request'
            model_id = self.env['request.maintenance.devices.printers'].search([('id', '=', rec.id)])
            self._send_activity(model_id, users, summary, note)

    def action_manager_approval(self):
        for rec in self:
            # if self.env.user == rec.employee_id.department_id.manager_id.user_id:
                rec.state = 'department_manager_approval'
                users = rec.employee_id.parent_id.user_id
                summary = 'Request Approve'
                note = 'You Should Approve This Request'
                model_id = self.env['request.maintenance.devices.printers'].search([('id', '=', rec.id)])
                self._send_activity(model_id, users, summary, note)
            # else:
            #     raise ValidationError(_('You Have no Permission to approve this'))

    def action_department_manager_approval(self):
        for rec in self:
#             if self.env.user == rec.employee_id.department_id.manager_id.user_id:
                rec.state = 'hr_approval'
                users = self.env['res.users'].search(
                [('groups_id', 'in', (self.env.ref('iet_hr_employee_enhancement.group_hr_officer').id,
                                      self.env.ref('iet_hr_employee_enhancement.group_hr_manager').id))])
                summary = 'Request Approve'
                note = 'You Should Approve This Request'
                model_id = self.env['request.maintenance.devices.printers'].search([('id', '=', rec.id)])
                self._send_activity(model_id, users, summary, note)
#             else:
#                 raise ValidationError(_('You Have no Permission to approve this'))

    def action_hr_approval(self):
        for rec in self:
            rec.state = 'it_approval'
            users = self.env['res.users'].search(
                [('groups_id', 'in', (self.env.ref('iet_hr_employee_enhancement.group_hr_officer').id,
                                      self.env.ref('iet_hr_employee_enhancement.group_hr_manager').id))])
            summary = 'Request Approve'
            note = 'You Should Approve This Request'
            model_id = self.env['request.maintenance.devices.printers'].search([('id', '=', rec.id)])
            self._send_activity(model_id, users, summary, note)

    def action_it_approval(self):
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
