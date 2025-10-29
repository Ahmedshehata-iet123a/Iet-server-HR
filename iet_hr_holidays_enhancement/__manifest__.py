# -*- coding: utf-8 -*-
{
    'name': "IET Time Off Enhancement",

    'summary': "Improving the employee leave management service through some additions by IET Company",

    'description': """
The Enhanced Time Off Addon is designed to provide a more comprehensive and user-friendly approach to
 managing employee time off. With its added features, reports, and customization options,
  this addon not only simplifies the approval process but also enhances overall organizational efficiency.
    """,

    'author': "IET",
    'website': "https://www.intelligent-experts.com/",

    'category': 'Human Resources/Time Off',
    'version': '18.0.0.0',

    'depends': ['base', 'hr', 'hr_holidays', 'hr_contract', 'iet_hr_employee_enhancement'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/return_vacation_view.xml',
        'views/hr_leave_view.xml',
        'views/flight_tickets_view.xml',
        'views/hr_employee_view.xml',
        'views/res_config_settings_views.xml',
        'report/leave_report.xml',
        'report/employee_time_off_report.xml',
        'wizards/employee_time_off_report_wizard.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'LGPL-3',

}
