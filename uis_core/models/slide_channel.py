from odoo import api, fields, models, _
from odoo.exceptions import UserError


@api.model
def _get_level_selection(self):
    return self.company_id.get_level_selection()


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'
    _rec_name = 'partner_id'

    lecture_attendance_count = fields.Integer()
    lectures_completion = fields.Float(compute="_compute_lectures_completion")
    course_level = fields.Selection(related='channel_id.level', store=True)
    total_grade = fields.Float(compute='_compute_total_grade', store=True)
    final_grade = fields.Float()
    mid_semester_grade = fields.Float()
    oral_grade = fields.Float()
    quizzes_total_grade = fields.Float()
    project_grade = fields.Float()
    assignments_grade = fields.Float()
    final_exam_grade_submitted = fields.Boolean()
    state = fields.Boolean()
    active = fields.Boolean(default=True)

    @api.constrains('final_grade')
    def _check_final_grade(self):
        for rec in self:
            if not (0 <= rec.final_grade <= rec.channel_id.final_exam_grade):
                raise UserError(f'Final grade must be between 0 and {rec.channel_id.final_exam_grade}')\
    @api.constrains('mid_semester_grade')
    def _check_mid_semester_grade(self):
        for rec in self:
            if not (0 <= rec.mid_semester_grade <= rec.channel_id.mid_semester_grade):
                raise UserError(f'Mid-semester grade must be between 0 and {rec.channel_id.mid_semester_grade}')

    @api.constrains('oral_grade')
    def _check_oral_grade(self):
        for rec in self:
            if not (0 <= rec.oral_grade <= rec.channel_id.oral_grade):
                raise UserError(f'Oral grade must be between 0 and {rec.channel_id.oral_grade}')

    @api.constrains('quizzes_total_grade')
    def _check_quizzes_total_grade(self):
        for rec in self:
            if not (0 <= rec.quizzes_total_grade <= rec.channel_id.quizzes_total_grade):
                raise UserError(f'Quizzes total grade must be between 0 and {rec.channel_id.quizzes_total_grade}')

    @api.constrains('project_grade')
    def _check_project_grade(self):
        for rec in self:
            if not (0 <= rec.project_grade <= rec.channel_id.project_grade):
                raise UserError(f'Project grade must be between 0 and {rec.channel_id.project_grade}')

    @api.constrains('assignments_grade')
    def _check_assignments_grade(self):
        for rec in self:
            if not (0 <= rec.assignments_grade <= rec.channel_id.assignments_grade):
                raise UserError(f'Assignments grade must be between 0 and {rec.channel_id.assignments_grade}')

    @api.onchange('lecture_attendance_count')
    def _compute_lectures_completion(self):
        for rec in self:
            rec.lectures_completion = round(
                100.0 * rec.lecture_attendance_count / (
                        rec.channel_id.actual_num_of_lectures or 1))

    def _record_manual_attendance(self):
        for rec in self:
            rec.lecture_attendance_count += 1

    @api.depends('final_grade', 'mid_semester_grade', 'oral_grade', 'quizzes_total_grade', 'assignments_grade',
                 'project_grade')
    def _compute_total_grade(self):
        for rec in self:
            rec.total_grade = rec.assignments_grade + rec.project_grade + rec.mid_semester_grade + rec.final_grade \
                              + rec.oral_grade + rec.quizzes_total_grade

    @api.onchange('final_grade')
    def _create_student_yearly_archive(self):
        std_channel_part_obj = self.env['slide.channel.partner']
        std_arch_line_obj = self.env['student.archive.line']
        slide_channel_obj = self.env['slide.channel']
        for rec in self:
            rec._origin.final_exam_grade_submitted = True
            passed = rec.total_grade >= (
                    rec.channel_id.total_grade * rec.channel_id.company_id.minimum_subject_passing_percentage)
            rec._origin.state = passed
            rec.state = passed

            rec.partner_id.write({'grade_archive_ids': [(0, 0, {
                'course_id': rec.channel_id.id,
                'level': rec.partner_id.level,
                'total_course_grade': rec.channel_id.total_grade,
                'student_grade': rec.total_grade,
                'partner_id': rec.partner_id.id,
                'state': 'pass' if passed else 'fail'
            })]})
            student_subjects = std_channel_part_obj.search(
                [('partner_id', '=', rec.partner_id.id), ('active', '=', True)])

            if len(student_subjects.filtered(lambda ss: not ss.final_exam_grade_submitted)) == 0:

                courses_passed = student_subjects.filtered(lambda ss: ss.state)
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
                rec.partner_id.grade_archive_ids = None
                levels = [code for code, name in rec.channel_id.company_id.get_level_selection()]

                slide_channel_partner_ids = std_channel_part_obj.search([('partner_id', '=', rec.partner_id.id),
                                                                         ('channel_id', 'in', courses_failed.ids)])

                for record in slide_channel_partner_ids:
                    record.lecture_attendance_count = 0
                    record.final_grade = 0
                    record.mid_semester_grade = 0
                    record.oral_grade = 0
                    record.quizzes_total_grade = 0
                    record.project_grade = 0
                    record.assignments_grade = 0
                    record.final_exam_grade_submitted = 0

                self.env.invalidate_all()

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
                        'company_id': rec.partner_id.company_id.id,
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
                    self.env['res.users'].search([('partner_id', '=', rec.partner_id.id)]).unlink()
                    rec.partner_id.active = False

                for course in courses_passed:
                    course.active = False


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    company_id = fields.Many2one('res.company', ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    academic_program_id = fields.Many2one('academic.program', required=True)
    department_id = fields.Many2one('department', required=True)
    semester_ids = fields.Many2many('semester')
    # course internal basic data
    code = fields.Char(required=True, copy=False)
    theoretical_hours = fields.Float()
    practical_hours = fields.Float()
    exercise_hours = fields.Float()
    num_of_weeks = fields.Float()
    num_of_lectures = fields.Integer()
    actual_num_of_lectures = fields.Integer(compute='_compute_actual_number_of_lectures', store=True)

    total_grade = fields.Float(compute='_compute_total_grade')  # FIXME: Make Sure That grades sum is consistent
    final_exam_grade = fields.Float()
    mid_semester_grade = fields.Float()
    oral_grade = fields.Float()
    quizzes_total_grade = fields.Float()
    project_grade = fields.Float()
    assignments_grade = fields.Float()
    level = fields.Selection(_get_level_selection, required=True, tracking=True)

    @api.depends('slide_ids.is_published')
    def _compute_actual_number_of_lectures(self):
        for rec in self:
            slide = rec.slide_ids.filtered('is_attendance')
            rec.actual_num_of_lectures += slide.is_published

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        slide_obj = self.env['slide.slide']
        for record in res:
            slide_obj.create({'name': '[{}] Attendance'.format(record.code),
                              'channel_id': record.id,
                              'slide_category': 'article',
                              'is_published': False,
                              'is_attendance': True
                              })
        return res

    @api.onchange('final_exam_grade', 'mid_semester_grade', 'oral_grade', 'quizzes_total_grade')
    def _compute_total_grade(self):
        for rec in self:
            rec.total_grade = rec.mid_semester_grade + rec.final_exam_grade + rec.oral_grade + rec.quizzes_total_grade

    @api.constrains('code')
    def _check_unique_code(self):
        for rec in self:
            if self.env['slide.channel'].search_count(
                    [('code', '=', rec.code.strip().replace(' ', '')), ('id', '!=', rec.id)]):
                raise UserError(_('Cannot create course with duplicated code'))

    # def action_channel_invite(self):
    #     self.ensure_one()
    #     template = self.env.ref('website_slides.mail_template_slide_channel_invite', raise_if_not_found=False)
    #
    #     local_context = dict(
    #         self.env.context,
    #         default_channel_id=self.id,
    #         default_use_template=bool(template),
    #         default_template_id=template and template.id or False,
    #         default_email_layout_xmlid='website_slides.mail_notification_channel_invite',
    #         default_partner_ids=self.env['res.partner'].search([('level', '=', self.level),
    #                                                             ('is_student', '=', True),
    #                                                             ('academic_program_id', '=',
    #                                                              self.academic_program_id.id)]).ids
    #     )
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'slide.channel.invite',
    #         'target': 'new',
    #         'context': local_context,
    #     }
