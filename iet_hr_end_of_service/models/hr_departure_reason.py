# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DepartureReasonCustom(models.Model):
    _inherit = "hr.departure.reason"

    # sequence = fields.Integer("Sequence", default=10)
    # name = fields.Char(string="Reason", required=True, translate=True)
    is_departure = fields.Boolean(string="Is Departure", )

    def _get_default_departure_reasons(self):
        return {
            'fired': self.env.ref('hr.departure_fired', False),
            'resigned': self.env.ref('hr.departure_resigned', False),
            'retired': self.env.ref('hr.departure_retired', False),
            'رفض العمل': self.env.ref('hr_payroll_customs.departure_no_work', False),
            'المادة ٨٠': self.env.ref('hr_payroll_customs.departure_number80', False),
            # 'انهاء العقد': self.env.ref('hr_payroll_customs.departure_end_contract', False),
            'طلب استثنائي': self.env.ref('hr_payroll_customs.departure_exceptional_request', False),
            'الاستقالة': self.env.ref('hr_payroll_customs.departure_resignation', False),
            'إنهاء العقد من قبل الشركة': self.env.ref('hr_payroll_customs.termination_of_the_contract_by_the_company', False),
            'إنهاء العقد': self.env.ref('hr_payroll_customs.end_of_the_contract', False),
        }

    # @api.ondelete(at_uninstall=False)
    # def _unlink_except_default_departure_reasons(self):
    #     ids = set(map(lambda a: a.id, self._get_default_departure_reasons().values()))
    #     if set(self.ids) & ids:
    #         raise UserError(_('Default departure reasons cannot be deleted.'))
