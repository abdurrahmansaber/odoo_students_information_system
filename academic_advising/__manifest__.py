# -*- coding: utf-8 -*-
{
    'name': "Academic Advising",

    'summary': """
        Academic Advising""",

    'description': """
        University Academic Advising
    """,

    'author': "Abdelrahman Khaled",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 11,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'sis_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/academic_advising_session_views.xml',
        'views/academic_advising_report_views.xml',
        'views/academic_advising_menus.xml',  # Last because referencing actions defined in previous files
    ],

    'application': True,
}
