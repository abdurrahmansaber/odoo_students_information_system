from odoo import api, fields, models


@api.model
def _get_level_selection(self):
    return self.company_id.get_level_selection()


class Section(models.Model):
    _name = 'section'
    _description = 'Section'
    _order = 'company_id, department_id, academic_program_id, level, name'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True, translate=True)
    department_id = fields.Many2one('department', required=True, ondelete='cascade')
    academic_program_id = fields.Many2one('academic.program', required=True, ondelete='cascade')
    level = fields.Selection(_get_level_selection, required=True)
    student_ids = fields.One2many('res.partner', 'section_id')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s (%s)' % (rec.name, dict(
                self.env['section'].fields_get(allfields=['level'])['level']['selection']
            ).get(rec.level))))
        return result
