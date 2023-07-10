from odoo import api, fields, models


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    partner_name = fields.Char(related='partner_id.name')
    partner_code = fields.Char(related='partner_id.internal_reference')
    partner_level = fields.Selection(related='partner_id.level', store=True)

    @api.onchange('final_exam_grade')
    def _create_student_yearly_archive(self):
        std_channel_part_obj = self.env['slide.channel.partner']
        std_grad_arch_obj = self.env['student_grade_archive']
        std_arch_line_obj = self.env['student.archive.line']
        slide_channel_obj = self.env['slide.channel']
        for rec in self:
            rec._origin.final_exam_grade_submitted = True
            passed = rec.total_grade >= (
                    rec.channel_id.total_grade * rec.channel_id.company_id.minimum_subject_passing_percentage)
            student_grade_archive_id = std_grad_arch_obj.create({
                'course_id': rec.channel_id.id,
                'level': rec.partner_id.level,
                'total_course_grade': rec.channel_id.total_grade,
                'student_grade': rec.total_grade,
                'partner_id': rec.partner_id.id,
                'state': 'pass' if passed else 'fail'
            })
            rec.partner_id.grade_archive_ids += student_grade_archive_id
            student_subjects = std_channel_part_obj.search([('partner_id', '=', rec.partner_id.id)])
            if len(student_subjects.filtered(lambda ss: not ss.final_exam_grade_submitted)) == 0:
                courses_passed = student_subjects.filtered(lambda ss: ss.state).mapped('channel_id')
                courses_failed = student_subjects.filtered(lambda ss: not ss.state).mapped('channel_id')

                state = (len(courses_failed) <= rec.channel_id.company_id.maximum_failed_subjects)

                total_subjects_grade = sum(student_subjects.mapped('total_grade'))

                vals = {
                    'partner_id': rec.partner_id.id,
                    'academic_year': rec.channel_id.company_id.academic_year_name,
                    'academic_program_id': rec.partner_id.academic_program_id.id,
                    'level': rec.partner_id.level,
                    'state': 'pass' if state else 'fail',
                    'total_grade': total_subjects_grade,
                    'section_id': rec.partner_id.section_id.name,
                    'academic_advisor_id': rec.partner_id.academic_advisor_id.id,
                    'course_grade_archive_ids': [(6, 0, rec.partner_id.grade_archive_ids.ids)]
                }

                std_arch_line_obj.create(vals)

                levels = [code for code, name in rec.channel_id.company_id.get_level_selection()]

                slide_channel_partner_ids = std_channel_part_obj.search([('partner_id', '=', rec.partner_id.id),
                                                                         ('channel_id', 'in', courses_failed.ids)])

                for record in slide_channel_partner_ids:
                    record.update({
                        'lecture_attendance_count': 0,
                        'final_exam_grade': 0,
                        'mid_semester_grade': 0,
                        'oral_grade': 0,
                        'quizzes_total_grade': 0,
                        'project_grade': 0,
                        'assignments_grade': 0,
                        'final_exam_grade_submitted': 0
                    })
                for course in courses_passed:
                    course._remove_membership(rec.partner_id)

                if state and not rec.partner_id.level == levels[-1]:
                    new_level = levels[levels.index(rec.partner_id.level) + 1]
                    courses_to_add = slide_channel_obj.search([('level', '=', new_level),
                                                               ('academic_program_id', '=',
                                                                rec.partner_id.academic_program_id.id)])
                    for course in courses_to_add:
                        course._action_add_members(rec.partner_id)

                    rec.partner_id.level = new_level

                if rec.partner_id.level == levels[-1] and state and not courses_failed:
                    vals = {
                        'student_name': rec.partner_id.name,
                        'company_id': rec.partner_id.company_id.name,
                        'student_code': rec.partner_id.internal_reference,
                        'national_id': rec.partner_id.national_id,
                        'phone': rec.partner_id.phone,
                        'email': rec.partner_id.email,
                        'lang': rec.partner_id.lang,
                        'street': rec.partner_id.street,
                        'city': rec.partner_id.city,
                        'state': rec.partner_id.state_id.name,
                        'country': rec.partner_id.country_id.name,
                        'line_ids': [(6, 0, rec.partner_id.archive_line_ids.ids)]
                    }
                    self.env['student.archive'].create(vals)
                    # TODO: Apply necessary logic for graduates
