# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_employee_return_date_lines = fields.Boolean(string="Return Vacation Date",
                                                          config_parameter='iet_hr_holidays_enhancement.hr_employee_return_date_lines')
