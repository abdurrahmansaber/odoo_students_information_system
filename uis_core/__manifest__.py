# -*- coding: utf-8 -*-
{
    'name': "UIS Core",

    'summary': """
        UIS Core""",

    'description': """
        University Information System (UIS) Core
    """,

    'author': "Abdelrahman Khaled",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 9,

    'external_dependencies': {'python': ['num2words']},

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'website_slides'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/slide_partner_cron.xml',

        # 'views/college_views.xml',
        'views/res_company_views.xml',
        'views/semester_views.xml',
        'views/res_config_settings_views.xml',
        'views/slide_channel.xml',
        'views/slide_channel_partner_views.xml',
        'views/department_views.xml',
        'views/academic_program_views.xml',
        'views/building_views.xml',
        'views/classroom_views.xml',
        'views/employee_views.xml',
    ],
    'application': True,
}
