# -*- coding: utf-8 -*-
{
    'name': 'Get Employee coordinates',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': """Get Employee coordinates.""",
    'description': """Get Employee coordinates.""",
    'author': 'Mahmoud Kousa',
    'company': '',
    'website': '',
    'depends': ['hr'],
    'data': [
        'views/hr_coordinate_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'get_employee_coordinates/static/src/js/geolocation_coordinates.js',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
