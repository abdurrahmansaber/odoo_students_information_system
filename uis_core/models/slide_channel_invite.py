from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SlideChannelInvite(models.TransientModel):
    _inherit = 'slide.channel.invite'

    def action_invite(self):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed """
        self.ensure_one()

        if not self.env.user.email:
            raise UserError(_("Unable to post message, please configure the sender's email address."))
        if not self.partner_ids:
            raise UserError(_("Please select at least one recipient."))

        mail_values = []
        for partner_id in self.partner_ids:
            slide_channel_partner = self.channel_id.channel_partner_ids.filtered(lambda cp: cp.partner_id == partner_id)
            if slide_channel_partner:
                mail_values.append(self._prepare_mail_values(slide_channel_partner))

        self.env['mail.mail'].sudo().create(mail_values)

        return {'type': 'ir.actions.act_window_close'}
