from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Classroom(models.Model):
    _name = 'classroom'
    _description = 'Classroom'
    _order = 'building_id, code'
    _parent_name = 'building_id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, translate=True)
    capacity = fields.Integer(required=True)
    building_id = fields.Many2one('building', required=True, ondelete='cascade')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s [%s]' % (rec.name, rec.code)))
        return result

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            classroom_ids = self.env['classroom'].search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if classroom_ids:
                raise ValidationError(_("Code %s already exists" % rec.code))

    @api.constrains('capacity')
    def _check_capacity(self):
        for rec in self:
            if rec.capacity < 0:
                raise ValidationError(_("Capacity must be 0 or higher"))
