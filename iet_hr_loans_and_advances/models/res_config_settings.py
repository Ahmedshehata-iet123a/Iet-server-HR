# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #loans
    journal_id_for_loans = fields.Many2one('account.journal', string='Journal',
                                           config_parameter='iet_hr_loans_and_advances.journal_id_for_loans')
    account_debit_for_loans = fields.Many2one('account.account', string='Debit Account',
                                              config_parameter='iet_hr_loans_and_advances.account_debit_for_loans')
    account_credit_for_loans = fields.Many2one('account.account', string='Credit Account',
                                               config_parameter='iet_hr_loans_and_advances.account_credit_for_loans')
    journal_id_reconcile_for_loans = fields.Many2one('account.journal', string='Journal',
                                                     config_parameter='iet_hr_loans_and_advances.journal_id_reconcile_for_loans')
    debit_reconcile_for_loans = fields.Many2one('account.account', string='Debit Account',
                                                config_parameter='iet_hr_loans_and_advances.debit_reconcile_for_loans')
    credit_reconcile_for_loans = fields.Many2one('account.account', string='Credit Account',
                                                 config_parameter='iet_hr_loans_and_advances.credit_reconcile_for_loans')
#loans
    journal_id_for_housing_advance = fields.Many2one('account.journal', string='Journal',
                                           config_parameter='iet_hr_loans_and_advances.journal_id_for_housing_advance')
    account_debit_for_housing_advance = fields.Many2one('account.account', string='Debit Account',
                                              config_parameter='iet_hr_loans_and_advances.account_debit_for_housing_advance')
    account_credit_for_housing_advance = fields.Many2one('account.account', string='Credit Account',
                                               config_parameter='iet_hr_loans_and_advances.account_credit_for_housing_advance')
    journal_id_reconcile_for_housing_advance = fields.Many2one('account.journal', string='Journal',
                                                     config_parameter='iet_hr_loans_and_advances.journal_id_reconcile_for_housing_advance')
    debit_reconcile_for_housing_advance = fields.Many2one('account.account', string='Debit Account',
                                                config_parameter='iet_hr_loans_and_advances.debit_reconcile_for_housing_advance')
    credit_reconcile_for_housing_advance = fields.Many2one('account.account', string='Credit Account',
                                                 config_parameter='iet_hr_loans_and_advances.credit_reconcile_for_housing_advance')

    # salary advances
    journal_id_for_salary_advances = fields.Many2one('account.journal', string='Journal',
                                                     config_parameter='iet_hr_loans_and_advances.journal_id_for_salary_advances')
    account_debit_for_salary_advances = fields.Many2one('account.account', string='Debit Account',
                                                        config_parameter='iet_hr_loans_and_advances.account_debit_for_salary_advances')
    account_credit_for_salary_advances = fields.Many2one('account.account', string='Credit Account',
                                                         config_parameter='iet_hr_loans_and_advances.account_credit_for_salary_advances')

