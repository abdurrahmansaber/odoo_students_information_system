from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AcademicAdvisingSession(models.Model):
    _name = 'academic.advising.session'
    _description = 'Academic Advising Session'
    _inherit = 'mail.thread'
    _rec_name = 'subject'
    _order = 'company_id, academic_advisor_id, date, start_time, end_time, subject'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    date = fields.Date(required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    academic_advisor_id = fields.Many2one('hr.employee', required=True)
    subject = fields.Char(required=True, translate=True)
    recommendations = fields.Text(translate=True)
    student_ids = fields.Many2many('res.partner')

    @api.constrains('start_time', 'end_time')
    def _check_start_time(self):
        for rec in self:
            if rec.start_time < 0.0 or 24.0 <= rec.start_time:
                raise ValidationError(_("Start Time must be between 00:00 and 23:59 inclusive"))

    @api.constrains('end_time')
    def _check_end_time(self):
        for rec in self:
            if rec.end_time <= rec.start_time:
                raise ValidationError(_("End Time must be greater than Start Time"))
            if rec.end_time < 0.0 or 24.0 <= rec.end_time:
                raise ValidationError(_("End Time must be between 00:00 and 23:59 inclusive"))

    @api.constrains('date', 'start_time', 'end_time', 'academic_advisor_id')
    def _check_academic_advisor_id(self):
        for rec in self:
            sessions = self.env['academic.advising.session'].search([
                ('date', '=', rec.date), ('end_time', '>', rec.start_time), ('start_time', '<', rec.end_time),
                ('academic_advisor_id', '=', rec.academic_advisor_id.id), ('id', '!=', rec.id)
            ])
            if sessions:
                raise ValidationError(_("Academic Advisor %s already busy at this time") % rec.academic_advisor_id.name)
