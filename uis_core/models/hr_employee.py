from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection(selection_add=[('teacher', 'Teacher')], ondelete={'teacher': 'set default'})


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # inheriting field name from hr.employee.base to enable translating name in hr.employee
    # because it's a related field
    name = fields.Char(translate=True)
