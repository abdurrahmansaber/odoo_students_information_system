from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


@api.model
def _get_semester_name_selection(self):
    return self.company_id.get_semester_name_selection()


class Semester(models.Model):
    _name = 'semester'
    _description = 'Semester'
    _order = 'company_id, start_date, end_date'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    name = fields.Selection(_get_semester_name_selection, required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, dict(
                self.env['semester'].fields_get(allfields=['name'])['name']['selection']
            ).get(rec.name)))
        return result

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            semesters = self.env['semester'].search([('name', '=', rec.name), ('company_id', '=', rec.company_id.id),
                                                     ('id', '!=', rec.id)])
            if semesters:
                raise ValidationError(_("%s Academic Year already has %s" % (
                    rec.company_id.academic_year_name, dict(
                        self.env['semester'].fields_get(allfields=['name'])['name']['selection']
                    ).get(rec.name)
                )))

    @api.constrains('start_date')
    def _check_start_date(self):
        for rec in self:
            if rec.start_date < rec.company_id.academic_year_start_date or \
               rec.start_date > rec.company_id.academic_year_end_date:
                raise ValidationError(_("Start Date of the Semester must be in the Academic Year period"))

    @api.constrains('end_date')
    def _check_end_date(self):
        for rec in self:
            if rec.end_date <= rec.start_date:
                raise ValidationError(_("End Date must be greater than Start Date"))
            if rec.end_date < rec.company_id.academic_year_start_date or \
               rec.end_date > rec.company_id.academic_year_end_date:
                raise ValidationError(_("End Date of the Semester must be in the Academic Year period"))

    @api.constrains('start_date', 'end_date')
    def _check_date_overlap(self):
        for rec in self:
            semesters = self.env['semester'].search([
                ('company_id', '=', rec.company_id.id), ('end_date', '>', rec.start_date),
                ('start_date', '<', rec.end_date), ('id', '!=', rec.id)
            ])
            if semesters:
                raise ValidationError(_("This semester overlaps with another semester"))
