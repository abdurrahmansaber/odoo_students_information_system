from odoo import http
from odoo.http import request


class OnboardingController(http.Controller):
    @http.route('/sis/student/courses', type='json', auth='user')
    def student_courses(self, uid: int):
        partner_id = request.env['res.users'].browse(uid).partner_id
        slide_channel_partner_ids = request.env['slide.channel.partner'].sudo().search([
            ('partner_id', '=', partner_id.id)
        ])
        slide_channel_ids = slide_channel_partner_ids.mapped('channel_id').filtered(
            lambda channel: channel.is_published and not channel.completed
        )

        student_courses = {}
        for channel_id in slide_channel_ids:
            slides = {}
            slide_ids = channel_id.slide_ids.filtered(lambda slide_id: slide_id.website_published)
            for slide_id in slide_ids:
                if not slide_id.is_category or slide_ids.filtered(lambda rec: rec.category_id == slide_id):
                    slides[slide_id.name] = {
                        'slide_category': dict(request.env['slide.slide'].sudo().fields_get(
                            allfields=['slide_category']
                        )['slide_category']['selection']).get(slide_id.slide_category),
                        'website_share_url': slide_id.website_share_url,
                        'video_url': slide_id.video_url,
                        'download': '%s/web/content/slide.slide/%s/binary_content?download=true' % (
                            request.env['ir.config_parameter'].sudo().get_param('web.base.url'), slide_id.id
                        ) if slide_id.slide_resource_downloadable else False,
                    }

            student_courses["{'website_url': '%s'}" % channel_id.website_url] = {
                'code': channel_id.code,
                'name': channel_id.name,
                'semesters': ', '.join(channel_id.semester_ids.mapped('name')),
                'level': dict(
                    request.env['slide.channel'].sudo().fields_get(allfields=['level'])['level']['selection']
                ).get(channel_id.level),
                'content': slides,
                'lectures_completion': slide_channel_partner_ids.filtered(
                    lambda rec: rec.channel_id == channel_id
                ).lectures_completion,
            }

        return student_courses