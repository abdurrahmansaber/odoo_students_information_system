from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Building(models.Model):
    _name = 'building'
    _description = 'Building'
    _order = 'company_id, department_id, code'
    _parent_name = 'department_id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, translate=True)
    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    department_id = fields.Many2one('department', required=True, ondelete='cascade')
    classroom_ids = fields.One2many('classroom', 'building_id')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s [%s]' % (rec.name, rec.code)))
        return result

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            building_ids = self.env['building'].search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if building_ids:
                raise ValidationError(_("Code %s already exists" % rec.code))
