import odoo
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.addons.web.controllers.session import Session


@http.route('/web/session/authenticate', type='http', auth="none", csrf=False)
def authenticate(self, db, login, password, base_location=None):
    if not http.db_filter([db]):
        raise AccessError("Database not found.")
    pre_uid = request.session.authenticate(db, login, password)
    if pre_uid != request.session.uid:
        # Crapy workaround for unupdatable Odoo Mobile App iOS (Thanks Apple :@) and Android
        # Correct behavior should be to raise AccessError("Renewing an expired session for user that has multi-factor-authentication is not supported. Please use /web/login instead.")
        return {'uid': None}

    request.session.db = db
    registry = odoo.modules.registry.Registry(db)
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, request.session.uid, request.session.context)
        if not request.db and not request.session.is_explicit:
            # request._save_session would not update the session_token
            # as it lacks an environment, rotating the session myself
            http.root.session_store.rotate(request.session, env)
            request.future_response.set_cookie(
                'session_id', request.session.sid,
                max_age=http.SESSION_LIFETIME, httponly=True
            )
        session_info = env['ir.http'].session_info()
        return str({'uid': session_info['uid']})


Session.authenticate = authenticate


class OnboardingController(http.Controller):
    @http.route('/sis/teacher/courses/<int:uid>', type='http', auth='user')
    def teacher_courses(self, uid):
        if request.session.uid != uid:
            raise AccessError("Access Denied")

        user_id = request.env['res.users'].sudo().browse(uid)

        teacher_courses = {}

        if user_id.partner_id.is_teacher:
            slide_channel_ids = request.env['slide.channel'].sudo().search([('user_id', '=', user_id.id)]).filtered(
                lambda channel: channel.is_published and not channel.completed
            )

            for channel_id in slide_channel_ids:
                slides = {}
                for slide_id in channel_id.slide_ids:
                    slides[slide_id.name] = {
                        'slide_category': dict(request.env['slide.slide'].sudo().fields_get(
                            allfields=['slide_category']
                        )['slide_category']['selection']).get(slide_id.slide_category),
                        'is_attendance': slide_id.is_attendance,
                        'website_published': slide_id.website_published,
                        'website_share_url': slide_id.website_share_url,
                        'video_url': slide_id.video_url,
                        'download': '%s/web/content/slide.slide/%s/binary_content?download=true' % (
                            request.env['ir.config_parameter'].sudo().get_param('web.base.url'), slide_id.id
                        ) if slide_id.slide_resource_downloadable else False,
                    }

                teacher_courses["{'website_url': '%s'}" % channel_id.website_url] = {
                    'code': channel_id.code,
                    'name': channel_id.name,
                    'semesters': ', '.join(channel_id.semester_ids.mapped('name')),
                    'level': dict(
                        request.env['slide.channel'].sudo().fields_get(allfields=['level'])['level']['selection']
                    ).get(channel_id.level),
                    'content': slides
                }

        return str(teacher_courses)

    @http.route('/sis/student/courses/<int:uid>', type='http', auth='user')
    def student_courses(self, uid):
        if request.session.uid != uid:
            raise AccessError("Access Denied")

        partner_id = request.env['res.users'].sudo().browse(uid).partner_id

        student_courses = {}

        if partner_id.is_student:
            slide_channel_partner_ids = request.env['slide.channel.partner'].sudo().search([
                ('partner_id', '=', partner_id.id)
            ])
            slide_channel_ids = slide_channel_partner_ids.mapped('channel_id').filtered(
                lambda channel: channel.is_published and not channel.completed
            )

            for channel_id in slide_channel_ids:
                slides = {}
                slide_ids = channel_id.slide_ids.filtered(lambda slide_id: slide_id.website_published)
                for slide_id in slide_ids:
                    if not slide_id.is_category or slide_ids.filtered(lambda rec: rec.category_id == slide_id):
                        slides[slide_id.name] = {
                            'slide_category': dict(request.env['slide.slide'].sudo().fields_get(
                                allfields=['slide_category']
                            )['slide_category']['selection']).get(slide_id.slide_category),
                            'is_attendance': slide_id.is_attendance,
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

        return str(student_courses)
