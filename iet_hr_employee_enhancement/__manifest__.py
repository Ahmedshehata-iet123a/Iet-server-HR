# -*- coding: utf-8 -*-
{
    'name': "IET HR Employee Enhancement",

    'summary': "Improving the employee and contract management service through some additions by IET Company",

    'description': """
The Employee and Contract Management Enhancement module is a valuable addition to any Odoo-based HR system.
 By automating contract expiration management, enriching employee and contract data,
  providing comprehensive report management capabilities, and introducing access rights, 
  this module helps businesses optimize their HR operations, improve overall efficiency, and ensure secure data management.
    """,

    'author': "IET",
    'website': "https://www.intelligent-experts.com/",

    'category': 'Human Resources/Employees',
    'version': '18.0.0.0',

    'depends': ['base', 'hr', 'account', 'hr_contract', 'mail', 'report_xlsx'],

    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/cron_for_expired_contracts.xml',
        'data/cron_to_create_employee_analytic.xml',
        'data/sequences.xml',
        'views/views.xml',
        'views/hr_employee_view.xml',
        'views/hr_contract_view.xml',
        'views/location_view.xml',
        'views/res_config_settings_views.xml',
        'reports/employees_sheet_views.xml',
        'reports/employee_analytic_report_views.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'LGPL-3',

}
