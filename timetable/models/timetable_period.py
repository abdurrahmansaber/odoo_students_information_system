from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TimetablePeriod(models.Model):
    _name = 'timetable.period'
    _description = 'Timetable Period'
    _rec_name = 'period_order'
    _order = 'company_id, timetable_id, start_time, end_time'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    timetable_id = fields.Many2one('timetable', required=True, ondelete='cascade')
    period_order = fields.Selection([('1st', 'First'), ('2nd', 'Second'), ('3rd', 'Third'), ('4th', 'Fourth'),
                                     ('5th', 'Fifth'), ('6th', 'Sixth'), ('7th', 'Seventh'), ('8th', 'Eighth'),
                                     ('9th', 'Ninth'), ('10th', 'Tenth'), ('11th', 'Eleventh'), ('12th', 'Twelfth')],
                                    required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, dict(
                self.env['timetable.period'].fields_get(allfields=['period_order'])['period_order']['selection']
            ).get(rec.period_order)))
        return result

    @api.constrains('name')
    def _check_period_order(self):
        for rec in self:
            periods = self.env['timetable.period'].search([
                ('period_order', '=', rec.period_order), ('timetable_id', '=', rec.timetable_id.id),
                ('id', '!=', rec.id)
            ])
            if periods:
                raise ValidationError(_("This Timetable already has %s Period" % (dict(
                    self.env['timetable.period'].fields_get(allfields=['period_order'])['period_order']['selection']
                ).get(rec.period_order))))

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

    @api.constrains('start_time', 'end_time')
    def _check_time_overlap(self):
        for rec in self:
            periods = self.env['timetable.period'].search([
                ('timetable_id', '=', rec.timetable_id.id), ('end_time', '>', rec.start_time),
                ('start_time', '<', rec.end_time), ('id', '!=', rec.id)
            ])
            if periods:
                raise ValidationError(_("This period overlaps with another period"))
