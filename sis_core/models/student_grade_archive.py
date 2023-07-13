from odoo import fields, models


class StudentGradeArchive(models.Model):
    _name = 'student.grade.archive'
    _rec_name = 'course_id'
    _description = 'Stores the grade of the student as triples, ' \
                   'course, complete score at the time the student was ' \
                   'enrolled in this course, student grade'

    course_id = fields.Many2one('slide.channel', readonly=True)
    level = fields.Char()
    archive_line_id = fields.Many2one('student.archive.line', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    total_course_grade = fields.Float(readonly=True)
    student_grade = fields.Float(readonly=True)
    state = fields.Char()
    minimum_passing_percentage = fields.Float(readonly=True, default=lambda
        self: self.course_id.company_id.minimum_subject_passing_percentage)
