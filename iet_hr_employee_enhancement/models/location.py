from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Location(models.Model):
    _name = 'location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Location Name', tracking=True)
    location_id = fields.Integer(string='Location Id', tracking=True)
    location_type = fields.Char(tracking=True)
    location_manager = fields.Many2one('hr.employee', tracking=True)
    location_timekeeper = fields.Many2one('hr.employee', tracking=True)
    location_timekeeper_2 = fields.Many2one('res.users', tracking=True)
    location_store_keeper = fields.Many2one('hr.employee', tracking=True)
    location_coordinates = fields.Char(tracking=True)
    generate_daily_documents = fields.Boolean(tracking=True)


    @api.constrains('location_id')
    def _check_unique_location_id(self):
        for record in self:
            if record.location_id:
                duplicate_records = self.search([('location_id', '=', record.location_id), ('id', '!=', record.id)])
                if duplicate_records:
                    raise ValidationError("Location Id must be unique!")


class LocationTransfer(models.Model):
    _name = 'location.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Location Transfer'

    name = fields.Char(tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved')], default='draft')
    relation_id3 = fields.Many2one('hr.employee', string='Employee', tracking=True)
    location_date = fields.Date(string='Date', required=False, tracking=True, default=fields.Date.today())
    original_location = fields.Many2one('location', string='Original Location', required=False, tracking=True)
    destination_location = fields.Many2one('location', string='Destination Location', required=False, tracking=True)
    location_user_id = fields.Many2one('res.users', string='User ID', required=False, tracking=True)

    @api.onchange('relation_id3')
    def get_original_location(self):
        for rec in self:
            if rec.relation_id3:
                rec.original_location = rec.relation_id3.location.id

    def action_submit(self):
        for rec in self:
            rec.relation_id3.location = rec.destination_location
            rec.state = 'submit'

    def action_approve(self):
        self.state = 'approve'

    def action_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('location.transfer') or '/'
        return super(LocationTransfer, self).create(vals)
