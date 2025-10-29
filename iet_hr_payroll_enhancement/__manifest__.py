# -*- coding: utf-8 -*-
{
    'name': "IET HR Payroll Enhancement",

    'summary': "Improving the employee payroll records management service through some additions by IET Company",

    'description': """
The Enhanced Payroll Addon is designed to elevate the Odoo Payroll experience by adding essential fields and
 improving computation processes. With its focus on accuracy, flexibility, and user experience,
  this addon empowers organizations to manage payroll more effectively while ensuring employee satisfaction and compliance.
    """,

    'author': "IET",
    'website': "https://www.intelligent-experts.com/",

    'category': 'Human Resources/Payroll',
    'version': '18.0.0.0',

    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll', 'hr_holidays', 'l10n_sa_hr_payroll', 'iet_hr_employee_enhancement',
                'iet_hr_holidays_enhancement'
                ],

    'data': [
        'data/cron_for_payroll_information.xml',
        'data/structure_rules.xml',
        # 'data/departure_reasons.xml',
        'security/ir.model.access.csv',
        'views/hr_contract.xml',
        'views/hr_payslip.xml',
        'report/payroll_report.xml',
        'wizard/payroll_excel_report_wizard_view.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',

    ],

    'installable': True,
    'application': False,
    'license': 'OEEL-1',

}
