from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Department(models.Model):
    _name = 'department'
    _description = 'Department'
    _order = 'company_id, code'
    _parent_name = 'company_id'

    code = fields.Char(required=True, translate=True)
    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    academic_program_ids = fields.One2many('academic.program', 'department_id')
    active = fields.Boolean(default=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '[%s] %s' % (rec.code, rec.name)))
        return result

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            department_ids = self.env['department'].search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if department_ids:
                raise ValidationError(_("Code %s already exists" % rec.code))
