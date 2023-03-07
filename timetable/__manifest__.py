# -*- coding: utf-8 -*-
{
    'name': "Timetable",

    'summary': """
        Timetable""",

    'description': """
        University Timetable
    """,

    'author': "Abdelrahman Khaled",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 11,

    # any module necessary for this one to work correctly
    'depends': ['base', 'sis_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/timetable_views.xml',
        'views/timetable_period_views.xml',
        'views/timetable_line_view.xml',

        'views/timetable_menus.xml',  # Last because referencing actions defined in previous files
    ],

    'application': True,
}
