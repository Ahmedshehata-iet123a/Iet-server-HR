# -*- coding: utf-8 -*-
{
    'name': "IET Loans And Salary Advances",

    'summary': """
        Improving the management of employee loans and salary advances within your organization""",

    'description': """
        The Loans and Salary Advances Addon revolutionizes the way organizations manage employee loans and salary advances.
         With its focus on user experience, streamlined processes, and comprehensive reporting,
          this addon not only simplifies financial management for HR but also supports employees in their financial needs.
           Empower your workforce with a transparent and efficient system that enhances financial well-being within your organization.
    """,

    'author': "IET",
    'website': "https://www.intelligent-experts.com/",

    'category': 'Human Resources/Employees',
    'version': '18.0.0.0',

    'depends': ['base', 'hr', 'account', 'hr_payroll', 'iet_hr_employee_enhancement', 'mail', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/loan_view.xml',
        'views/salary_advance_view.xml',
        'views/housing_advance.xml',
        'views/hr_pyslib_view.xml',
        'views/res_config_settings_views.xml',
        'report/advance_report.xml',
        'report/loans_and_addvance_report.xml',
        'report/report_action_for_excel.xml',
    ],

    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
