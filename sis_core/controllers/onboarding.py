from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


class OnboardingController(http.Controller):
    @http.route('/sis/user/info/<int:uid>', type='http', auth='user')
    def user_info(self, uid):
        if request.session.uid != uid:
            raise AccessError("Access Denied")

        user_id = request.env['res.users'].sudo().browse(uid)
        partner_id = user_id.partner_id

        user_info = {
            'name': partner_id.name,
            'phone': partner_id.phone,
            'email': partner_id.email,
            'user_context': dict(request.env['res.users'].context_get()),
            'college': (
                f'[{partner_id.company_id.code}] ' if partner_id.company_id.code else ""
            ) + partner_id.company_id.name,
        }

        if partner_id.is_student:
            user_info.update({
                'department': partner_id.department_id.name_get()[0][1],
                'academic_program': partner_id.academic_program_id.name_get()[0][1],
                'level': dict(
                    request.env['res.partner'].sudo().fields_get(allfields=['level'])['level']['selection']
                ).get(partner_id.level),
                'section_id': partner_id.section_id.name,
                'is_student': partner_id.is_student,
                'student_id': partner_id.internal_reference,
                'national_id': partner_id.national_id,
            })

        elif partner_id.is_teacher:
            employee_id = user_id.employee_ids[0]
            user_info.update({
                'is_teacher': partner_id.is_teacher,
                'job_title': employee_id.job_title,
                'tags': ', '.join(employee_id.category_ids.mapped('name')),
            })

        return str(user_info)
