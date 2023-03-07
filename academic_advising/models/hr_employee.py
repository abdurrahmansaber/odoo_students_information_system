from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    academic_advisee_ids = fields.One2many('res.partner', 'academic_advisor_id')
