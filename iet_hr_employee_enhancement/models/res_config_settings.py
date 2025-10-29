# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_employee_insurance_information = fields.Boolean(string="Insurance Information",
                                                       config_parameter='iet_hr_employee_enhancement.hr_employee_insurance_information')
    hr_employee_work_uniform_measurement = fields.Boolean(string="Work Uniform Measurement",
                                                       config_parameter='iet_hr_employee_enhancement.hr_employee_work_uniform_measurement')

