from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class College(models.Model):
    _name = 'college'
    _description = 'College'
    _order = 'code'

    code = fields.Char(required=True, translate=True)
    name = fields.Char(required=True, translate=True)
    department_ids = fields.One2many('department', 'college_id')
    active = fields.Boolean(default=True)

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            college_ids = self.env['college'].search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if college_ids:
                raise ValidationError(_("Code %s already exists" % rec.code))
