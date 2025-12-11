{
    'name': 'IET KSA Payroll Custom Rules',
    'version': '18.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Override KSA Payroll Rules with Custom Equations',
    'description': """
    This module overrides standard KSA payroll rules and adds new allowances/deductions 
    based on custom logic provided.
    It includes logic for:
    - Prorated Allowances (Housing, Transport, Food, Phone).
    - Complex GOSI calculation based on dates.
    - Custom End of Service Calculation.
    - Attendance Deductions (Late, Early, Absence).
    """,
    'depends': ['iet_hr_payroll_enhancement', 'iet_hr_end_of_service'],
    'data': [
        'data/ksa_saudi_employee_payroll_structure.xml',
        'data/ksa_expact_employee_payroll_structure.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}