from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_teacher = fields.Boolean(help='technical field used in domain filtering')

