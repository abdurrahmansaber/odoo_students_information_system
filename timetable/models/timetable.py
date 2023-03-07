from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Timetable(models.Model):
    _name = 'timetable'
    _description = 'Timetable'
    _order = 'company_id, department_id, academic_program_id, semester'

    semester = fields.Many2one('semester', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    department_id = fields.Many2one('department', required=True, ondelete='cascade')
    academic_program_id = fields.Many2one('academic.program', required=True, ondelete='cascade')
    is_created = fields.Boolean(default=False)
    timetable_periods = fields.One2many('timetable.period', 'timetable_id')
    periods_count = fields.Integer(compute='_compute_periods_count')
    saturday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'saturday')])
    sunday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'sunday')])
    monday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'monday')])
    tuesday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'tuesday')])
    wednesday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'wednesday')])
    thursday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'thursday')])
    friday_lines = fields.One2many('timetable.line', 'timetable_id', domain=[('weekday', '=', 'friday')])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['is_created'] = True
        res = super().create(vals_list)
        return res

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s, %s (%s)' % (
                rec.academic_program_id.name, rec.department_id.name, rec.semester.name_get()[0][1]
            )))
        return result

    def _compute_periods_count(self):
        for rec in self:
            rec.periods_count = len(rec.timetable_periods)

    @api.constrains('semester', 'department_id', 'academic_program_id')
    def _check_duplication(self):
        for rec in self:
            timetable_ids = self.env['timetable'].search([('semester', '=', rec.semester.id),
                                                          ('company_id', '=', rec.company_id.id),
                                                          ('department_id', '=', rec.department_id.id),
                                                          ('academic_program_id', '=', rec.academic_program_id.id),
                                                          ('id', '!=', rec.id)])
            if timetable_ids:
                raise ValidationError(_("This timetable already exists"))

    def action_open_timetable_periods(self):
        return {
            'name': _('Timetable Periods'),
            'type': 'ir.actions.act_window',
            'res_model': 'timetable.period',
            'view_mode': 'tree',
            'views': [[self.env.ref('timetable.view_timetable_periods_tree').id, 'tree']],
            'context': {'default_company_id': self.company_id.id, 'default_timetable_id': self.id},
            'domain': [('company_id', 'in', self.env.context['allowed_company_ids']), ('timetable_id', '=', self.id)],
            'target': 'current',
        }
