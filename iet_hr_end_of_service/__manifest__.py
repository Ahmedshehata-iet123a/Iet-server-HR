# -*- coding: utf-8 -*-
{
    'name': "IET HR End Of Service",

    'summary': "Improving the employee End Of Service process through some additions by IET Company",

    'description': """
The Enhanced Employee End of Service Addon is designed to optimize the resignation and clearance processes,
 ensuring a smooth and efficient transition for departing employees. By improving communication, automating workflows,
  and providing comprehensive reporting, this addon enhances the overall employee experience while supporting HR in managing transitions effectively.
   Empower your organization with a streamlined process that prioritizes both employee satisfaction and operational efficiency.
    """,

    'author': "IET",
    'website': "https://www.intelligent-experts.com/",

    'category': 'Human Resources/Payroll',
    'version': '18.0.0.0',

    'depends': ['base', 'hr', 'hr_holidays', 'hr_appraisal', 'hr_contract', 'iet_hr_employee_enhancement',
                'iet_hr_holidays_enhancement'],

    'data': [
        'security/ir.model.access.csv',
        'data/departure_reasons.xml',
        'views/resignation_request.xml',
        'views/clearance.xml',
    ],

    'license': 'LGPL-3',
    'installable': True,
    'application': False,

}
