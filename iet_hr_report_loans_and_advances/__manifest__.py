{
    'name': "Iet Hr Report loans_and_advances",
    'summary': """ iet_hr_report_loans_and_advances  """,
    'description': """ """,
    'author': "Ahmed Shehata",
    'website': 'https://intelligent-experts.com/en/home/',
    'version': '18.0.0.1.0',
    'depends': [
        'iet_hr_loans_and_advances',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/action_loans_report_excel.xml',
        'wizard/wizard.xml',
        'views/base_menus.xml',

    ],
}
