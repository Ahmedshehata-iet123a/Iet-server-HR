# -*- coding: utf-8 -*-
{
    'name': "IET HR Services",

    'summary': """
        provides a centralized platform for managing employee requests and tasks,
         automating workflows, and enhancing productivity.
          With its user-friendly interface and customizable features,
           this module is an essential tool for any organization seeking to streamline its internal processes.
    """,
    'description': """
        Provides a comprehensive platform for employees to submit various requests and tasks,
         streamlining internal processes and enhancing productivity. The module covers a wide range of requests, including:
            - Employee Transfer Request
            - Letter Definition Request
            - Transaction Certification Request
            - Maintenance Requests for Devices and Printers
            - Maintenance Requests for Plumbing and Electricity
            - Salary Account Change Request
            - Office Supplies Request
            - Task Assignment for External Work
        """,


    'author': "IET",
    'website': "https://www.intelligent-experts.com",
    'category': 'Human Resources/Employees',
    'version': '18.0.0.0',
    'depends': ['base', 'mail', 'iet_hr_employee_enhancement'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/request_to_specify_letter_view.xml',
        'views/request_to_document_transaction_view.xml',
        'views/request_plumbing_and_electrical_view.xml',
        'views/request_office_supplies_view.xml',
        'views/others_views.xml',
        'views/request_transfer_employee_views.xml',
        'views/request_change_salary_account_view.xml',
        'views/assignment_to_external_work_view.xml',
        'views/request_maintenance_devices_printers_view.xml',
        'views/menu_items_views.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}
