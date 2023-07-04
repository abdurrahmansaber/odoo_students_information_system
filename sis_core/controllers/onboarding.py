from odoo import http
from odoo.http import request


class OnboardingController(http.Controller):
    @http.route('/sis/user/info/<int:uid>', type='http', auth='user')
    def user_info(self, uid):
        user_id = request.env['res.users'].browse(uid)
        partner_id = user_id.partner_id
        return str({
            'name': user_id.name,
            'is_student': user_id.is_student,
            'student_id': partner_id.internal_reference,
            'national_id': partner_id.national_id,
            'phone': partner_id.phone,
            'email': partner_id.email,
            'college': (
                f'[{partner_id.company_id.code}] ' if partner_id.company_id.code else ""
            ) + partner_id.company_id.name,
            'department': partner_id.department_id.name_get()[0][1],
            'academic_program': partner_id.academic_program_id.name_get()[0][1],
            'level': dict(
                request.env['res.partner'].fields_get(allfields=['level'])['level']['selection']
            ).get(partner_id.level),
            'section_id': partner_id.section_id.name,
        })
