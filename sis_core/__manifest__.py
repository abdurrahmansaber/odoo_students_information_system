# -*- coding: utf-8 -*-
{
    'name': "SIS Core",

    'summary': """
        SIS Core""",

    'description': """
        Students Information System (SIS) Core
    """,

    'author': "Abdelrahman Khaled",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 10,

    # any module necessary for this one to work correctly
    'depends': ['base', 'uis_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/student_views.xml',
        'views/student_archive_views.xml',
        'views/section_views.xml',
        'views/slide_channel_partner_views.xml',

        'views/sis_menus.xml',  # Last because referencing actions defined in previous files
    ],

    'application': True,
}
