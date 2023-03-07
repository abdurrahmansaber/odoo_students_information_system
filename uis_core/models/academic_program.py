from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AcademicProgram(models.Model):
    _name = 'academic.program'
    _description = 'Academic Program'
    _order = 'company_id, department_id, code'
    _parent_name = 'department_id'

    code = fields.Char(required=True, translate=True)
    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    department_id = fields.Many2one('department', required=True, ondelete='cascade')
    active = fields.Boolean(default=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '[%s] %s' % (rec.code, rec.name)))
        return result


    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            academic_program_ids = self.env['academic.program'].search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if academic_program_ids:
                raise ValidationError(_("Code %s already exists" % rec.code))
