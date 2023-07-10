from odoo import api, fields, models


class StudentArchive(models.Model):
    _name = 'student.archive'
    _description = 'Student History'

    student_name = fields.Char()
    company_id = fields.Char()
    student_code = fields.Char(help='unique internal id for students')
    national_id = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    lang = fields.Char()
    street = fields.Char()
    city = fields.Char()
    state = fields.Char()
    country = fields.Char()
    line_ids = fields.One2many('student.archive.line', 'archive_id')


class StudentArchiveLine(models.Model):
    _name = 'student.archive.line'

    archive_id = fields.Many2one('student.archive')
    company_id = fields.Many2one('res.company', string='Company')
    partner_id = fields.Many2one('res.partner')
    academic_advisor_id = fields.Many2one('hr.employee', ondelete='restrict')
    academic_year = fields.Char()
    academic_program_id = fields.Many2one(comodel_name='academic.program', ondelete='restrict')
    level = fields.Char()
    state = fields.Char()
    total_grade = fields.Float()
    course_grade_archive_ids = fields.One2many('student.grade.archive', 'archive_line_id')
    section_id = fields.Char()
