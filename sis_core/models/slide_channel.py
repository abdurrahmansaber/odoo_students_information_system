from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    def _remove_membership(self, partner_ids):
        grade_archive_ids = self.env['student.grade.archive'].search([('course_id', '=', self.id),
                                                                      ('partner_id', 'in', partner_ids.ids),
                                                                      ('state', '=', 'pass')])
        if not grade_archive_ids:
            raise ValidationError('There is no record of this student passing this course!')

        super(SlideChannel, self)._remove_membership(partner_ids)

    def _action_add_members(self, target_partners, **member_values):
        super(SlideChannel, self)._action_add_members(target_partners, **member_values)

        grade_archive_ids = self.env['student.grade.archive'].search([('course_id', '=', self.id),
                                                                      ('partner_id', 'in', target_partners.ids),
                                                                      ('state', '=', 'pass')])
        if grade_archive_ids:
            raise ValidationError('This student has already passed this course!')

        for partner in target_partners:
            if self:
                self.env['slide.slide.partner'].create({
                    'slide_id': self.slide_ids.filtered('is_attendance').id,
                    'partner_id': partner.id
                })

    def action_redirect_to_members(self, completed=False):
        """ Redirects to attendees of the course. If completed is True, a filter
        will be added in action that will display only attendees who have completed
        the course. """
        action_ctx = {'active_test': False}
        action = self.env["ir.actions.actions"]._for_xml_id("website_slides.slide_channel_partner_action")
        if completed:
            action_ctx['search_default_filter_completed'] = 1
        action['domain'] = [('channel_id', 'in', self.ids), ('channel_user_id', '=', self.env.user.id),
                            ('partner_id.is_student', "=", True)]
        action['sample'] = 1
        if completed:
            help_message = {'header_message': _("No Attendee has completed this course yet!"), 'body_message': ""}
        else:
            help_message = {
                'header_message': _("No Attendees Yet!"),
                'body_message': _("From here you'll be able to monitor attendees and to track their progress.")
            }
        action[
            'help'] = """<p class="o_view_nocontent_smiling_face">%(header_message)s</p><p>%(body_message)s</p>""" % help_message
        if len(self) == 1:
            action['display_name'] = _('Attendees of %s', self.name)
            action_ctx['search_default_channel_id'] = self.id
        action['context'] = action_ctx
        return action

    @api.depends('channel_partner_ids.channel_id')
    def _compute_members_count(self):
        read_group_res = self.env['slide.channel.partner'].sudo()._read_group([('channel_id', 'in', self.ids),
                                                                               ('partner_id.is_student', '=', True)],
                                                                              ['channel_id'], 'channel_id')
        data = dict((res['channel_id'][0], res['channel_id_count']) for res in read_group_res)
        for channel in self:
            channel.members_count = data.get(channel.id, 0)
