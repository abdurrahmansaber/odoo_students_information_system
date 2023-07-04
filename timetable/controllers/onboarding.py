from odoo import http
from odoo.http import request
from datetime import date


class OnboardingController(http.Controller):
    @http.route('/sis/student/timetable', type='json', auth='user')
    def student_timetable(self, uid: int):
        semester = request.env['semester'].sudo().search([
            ('company_id', '=', request.env.company.id),
            ('start_date', '<=', date.today()),
            ('end_date', '>=', date.today()),
        ], limit=1)
        partner_id = request.env['res.users'].browse(uid).partner_id
        slide_channel_ids = request.env['slide.channel.partner'].sudo().search([
            ('partner_id', '=', partner_id.id)
        ]).mapped('channel_id').filtered(lambda channel: channel.is_published and not channel.completed).ids

        timetable = request.env['timetable'].sudo().search([
            ('semester', '=', semester.id),
            ('department_id', '=', partner_id.department_id.id),
            ('academic_program_id', '=', partner_id.academic_program_id.id)
        ])
        weekdays = [
            ('saturday', timetable.saturday_lines),
            ('sunday', timetable.sunday_lines),
            ('monday', timetable.monday_lines),
            ('tuesday', timetable.tuesday_lines),
            ('wednesday', timetable.wednesday_lines),
            ('thursday', timetable.thursday_lines),
            ('friday', timetable.friday_lines)
        ]

        student_timetable = {}
        for weekday in weekdays:
            weekday_lines = {}
            for line in weekday[1].filtered(
                lambda line: line.course_id.id in slide_channel_ids and partner_id.section_id.id in line.section_ids.ids
            ):
                weekday_lines["{'level': '%s', 'section': '%s', 'timetable_period': '%s'}" % (
                    line.level, ', '.join(line.section_ids.mapped('name')), line.timetable_period.period_order
                )] = {
                    'course': line.course_id.name,
                    'teacher': line.teacher_id.name,
                    'type': line.type,
                    'building': line.building_id.name,
                    'classroom': line.classroom_id.name,
                }
            student_timetable[weekday[0]] = weekday_lines
        return {"{'semester': '%s'}" % semester.name: student_timetable}
