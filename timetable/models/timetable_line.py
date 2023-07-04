from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


@api.model
def _get_level_selection(self):
    return self.timetable_id.company_id.get_level_selection()


class TimetableLine(models.Model):
    _name = 'timetable.line'
    _description = 'Timetable Line'
    _parent_name = 'timetable_id'

    timetable_id = fields.Many2one('timetable', required=True, ondelete='cascade')
    weekday = fields.Selection([('saturday', 'Saturday'), ('sunday', 'Sunday'), ('monday', 'Monday'),
                                ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
                                ('friday', 'Friday')], required=True)
    timetable_period = fields.Many2one('timetable.period', required=True)
    level = fields.Selection(_get_level_selection, required=True)
    course_id = fields.Many2one('slide.channel', required=True, ondelete='cascade')
    teacher_id = fields.Many2one('hr.employee', required=True)
    type = fields.Selection([('lecture', 'Lecture'), ('tutorial', 'Tutorial'), ('practical', 'Practical')],
                            required=True)
    section_ids = fields.Many2many('section', required=True)
    building_id = fields.Many2one('building', required=True)
    classroom_id = fields.Many2one('classroom', required=True)

    @api.onchange('level')
    def _onchange_level(self):
        for rec in self:
            rec.section_ids = self.env['section'].search([
                ('department_id', '=', rec.timetable_id.department_id.id),
                ('academic_program_id', '=', rec.timetable_id.academic_program_id.id),
                ('level', '=', rec.level),
            ])

    @api.constrains('teacher_id')
    def _check_teacher_id(self):
        for rec in self:
            lines = self.env['timetable.line'].search([('timetable_id', '=', rec.timetable_id.id),
                                                       ('weekday', '=', rec.weekday),
                                                       ('timetable_period', '=', rec.timetable_period.id),
                                                       ('teacher_id', '=', rec.teacher_id.id),
                                                       ('id', '!=', rec.id)])
            if lines:
                raise ValidationError(
                    _("Teacher %s can't teach more than class at the same time") % rec.teacher_id.name
                )

    @api.constrains('classroom_id')
    def _check_classroom_id(self):
        for rec in self:
            lines = self.env['timetable.line'].search([('timetable_id', '=', rec.timetable_id.id),
                                                       ('weekday', '=', rec.weekday),
                                                       ('timetable_period', '=', rec.timetable_period.id),
                                                       ('classroom_id', '=', rec.classroom_id.id),
                                                       ('id', '!=', rec.id)])
            if lines:
                raise ValidationError(
                    _("Classroom %s can't be occupied by more than class at the same time") % rec.classroom_id.name
                )

    @api.constrains('section_ids')
    def _check_section_ids(self):
        for rec in self:
            lines = self.env['timetable.line'].search_read([('timetable_id', '=', rec.timetable_id.id),
                                                            ('weekday', '=', rec.weekday),
                                                            ('timetable_period', '=', rec.timetable_period.id),
                                                            ('section_ids', 'in', rec.section_ids.ids),
                                                            ('id', '!=', rec.id)], ['section_ids'])

            if lines:
                raise ValidationError(_("Section(s) [%s] can't be in more than class at the same time") % ', '.join(
                    self.env['section'].browse(list(set(rec.section_ids.ids).intersection(
                        {section for line in lines for section in line['section_ids']}
                    ))).mapped('name')
                ))
