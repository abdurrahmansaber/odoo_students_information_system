from odoo import api, fields, models, _
from odoo.exceptions import UserError


@api.model
def _get_level_selection(self):
    return self.company_id.get_level_selection()


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    lecture_attendance_count = fields.Integer()
    lectures_completion = fields.Float(compute="_compute_lectures_completion")
    partner_name = fields.Char(compute="_compute_partner_data")
    partner_code = fields.Char(compute="_compute_partner_data")

    @api.depends('partner_id')
    def _compute_partner_data(self):
        for rec in self:
            rec.partner_name = rec.partner_id.name
            rec.partner_code = rec.partner_id.internal_reference

    @api.onchange('lecture_attendance_count')
    def _compute_lectures_completion(self):
        for rec in self:
            rec.lectures_completion = round(
                100.0 * rec.lecture_attendance_count / (rec.channel_id.num_of_lectures or 1)) if rec.lecture_attendance_count <= rec.channel_id.num_of_lectures else 100

    def _record_manual_attendance(self):
        for rec in self:
            rec.lecture_attendance_count += 1


# This is the course model , blame odoo for the ambiguity :)
class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    company_id = fields.Many2one('res.company', ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    academic_program_id = fields.Many2one('academic.program', required=True)
    semester_ids = fields.Many2many('semester')
    # course internal basic data
    code = fields.Char(required=True, copy=False)
    theoretical_hours = fields.Float()
    practical_hours = fields.Float()
    exercise_hours = fields.Float()
    num_of_weeks = fields.Float()
    num_of_lectures = fields.Integer()

    total_grade = fields.Float(compute='_compute_total_grade')  # FIXME: Make Sure That grades sum is consistent
    final_exam_grade = fields.Float()
    mid_semester_grade = fields.Float()
    oral_grade = fields.Float()
    quizzes_total_grade = fields.Float()
    project_grade = fields.Float()
    assignments_grade = fields.Float()
    level = fields.Selection(_get_level_selection, required=True,
                             tracking=True)

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

    def action_channel_invite(self):
        self.ensure_one()
        template = self.env.ref('website_slides.mail_template_slide_channel_invite', raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_channel_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_email_layout_xmlid='website_slides.mail_notification_channel_invite',
            default_partner_ids=self.env['res.partner'].search([('level', '=', self.level),
                                                                ('is_student', '=', True),
                                                                ('academic_program_id', '=',
                                                                 self.academic_program_id.id)]).ids
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'slide.channel.invite',
            'target': 'new',
            'context': local_context,
        }
