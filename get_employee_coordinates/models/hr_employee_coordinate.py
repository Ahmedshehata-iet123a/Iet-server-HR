# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployeeCoordinate(models.Model):
    _name = 'hr.employee.coordinate'
    _description = 'Hr Employee Coordinate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Location Name", required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees", required=True, tracking=True)
    distance = fields.Float(string="Distance (M2)", required=True, tracking=True)
    latitude = fields.Float(string="Latitude", tracking=True, digits=(2, 7))
    longitude = fields.Float(string="Longitude", tracking=True, digits=(3, 7))
    company_id = fields.Many2one('res.company', store=True, readonly=False,
                                 default=lambda self: self.env.company, required=True)

    def action_get_coordinates(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.client',
            'tag': 'get_employee_coordinates',
        }

    @api.model
    def save_coordinates(self, active_id, latitude, longitude):
        record = self.browse(active_id)
        record.write({
            'latitude': latitude,
            'longitude': longitude,
        })

    def action_open_google_maps(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.google.com/maps',
            'target': 'new',
        }
