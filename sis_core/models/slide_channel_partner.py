from odoo import api, fields, models


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    partner_name = fields.Char(related='partner_id.name')
    partner_code = fields.Char(related='partner_id.internal_reference')
