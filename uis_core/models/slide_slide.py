from odoo import api, fields, models


class SlidePartnerRelation(models.Model):
    _inherit = 'slide.slide.partner'

    def write(self, values):
        res = super(SlidePartnerRelation, self).write(values)
        if 'completed' in values and self.slide_id.is_attendance:
            attended = self.env['slide.channel.partner'].search(
                [('channel_id', '=', self.channel_id.id), ('partner_id', '=', self.partner_id.id)])

            for rec in attended:
                if not self._context.get('cron_job'):
                    rec.lecture_attendance_count += 1

        else:
            slides_completion_to_recompute = self.env['slide.slide.partner']
            if 'completed' in values:
                slides_completion_to_recompute = self.filtered(
                    lambda slide_partner: slide_partner.completed != values['completed'])

            if slides_completion_to_recompute:
                slides_completion_to_recompute._recompute_completion()
        return res

    def _compute_attendance_complete_state(self):
        records = self.env['slide.slide.partner'].search([]).filtered(
            lambda sl: sl.slide_id.is_attendance).with_context(cron_job=True)
        for rec in records:
            rec.sudo().update({'completed': False})


class Slide(models.Model):
    _inherit = 'slide.slide'

    is_attendance = fields.Boolean(default=False)

    @api.depends('slide_category', 'question_ids', 'channel_id.is_member', 'is_published')
    @api.depends_context('uid')
    def _compute_mark_complete_actions(self):
        for slide in self:
            if slide.is_attendance:
                slide.can_self_mark_uncompleted = False
                slide.can_self_mark_completed = (
                        slide.website_published
                        and slide.channel_id.is_member
                        and slide.slide_category != 'quiz'
                        and not slide.question_ids
                )
            else:
                slide.can_self_mark_uncompleted = slide.website_published and slide.channel_id.is_member
                slide.can_self_mark_completed = (
                        slide.website_published
                        and slide.channel_id.is_member
                        and slide.slide_category != 'quiz'
                        and not slide.question_ids
                )


