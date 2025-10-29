# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    company_id = fields.Many2one('res.company')

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('is_on_vacation', '=', False)]


    @api.depends('company_id', 'department_id', )
    def _compute_employee_ids(self):
        for wizard in self:
            domain = wizard._get_available_contracts_domain()
            if wizard.department_id:
                domain = expression.AND([
                    domain,
                    [('department_id', 'child_of', self.department_id.id)]
                ])
            if wizard.company_id:
                domain = expression.AND([
                    domain,
                    [('company_id', 'child_of', self.company_id.id)]
                ])
            wizard.employee_ids = self.env['hr.employee'].search(domain)
