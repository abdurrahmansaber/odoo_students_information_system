from num2words import num2words
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    code = fields.Char(required=True, translate=True)
    study_duration = fields.Integer(required=True, default=4)
    preparatory_year_included = fields.Boolean(required=True, default=False)
    department_ids = fields.One2many('department', 'company_id')
    academic_year_name = fields.Char(compute='_compute_academic_year_name')
    academic_year_code = fields.Char(translate=True)
    academic_year_start_date = fields.Date(default=fields.Date.today)
    academic_year_end_date = fields.Date()
    academic_year_number_of_semesters = fields.Integer(default=2)
    minimum_subject_passing_percentage = fields.Float(defualt=0.5)
    maximum_failed_subjects = fields.Integer(default=2)

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            company_ids = self.env['res.company'].search([('code', '=', rec.code), ('id', '!=', rec.id)])
            if company_ids:
                raise ValidationError(_("Code %s already exists" % rec.code))

    @api.constrains('study_duration')
    def _check_study_duration(self):
        for rec in self:
            if rec.study_duration < 2:
                raise ValidationError(_("Study Duration must be greater than 1"))

    @api.model
    @tools.ormcache()
    def get_level_selection(self):
        def ordinal(n: int):
            return 'th' if 11 <= (n % 100) <= 13 else ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        selection_list = []
        company_id = self.env['res.company'].browse(
            self.env.context.get('allowed_company_ids')[0]
        ) if self.env.context.get('allowed_company_ids') else self.env.company
        for i in range(1, company_id.study_duration + (not company_id.preparatory_year_included)):
            selection_list.append((f'{i}{ordinal(i)}', _(num2words(i, ordinal=True).capitalize())))
        return ([('preparatory', 'Preparatory')] if company_id.preparatory_year_included else []) + selection_list

    @api.depends('academic_year_start_date', 'academic_year_end_date')
    def _compute_academic_year_name(self):
        for rec in self:
            if rec.academic_year_start_date and rec.academic_year_end_date:
                rec.academic_year_name = str(rec.academic_year_start_date.year) \
                    if rec.academic_year_start_date.year == rec.academic_year_end_date.year \
                    else f'{rec.academic_year_start_date.year} / {rec.academic_year_end_date.year}'
            else:
                rec.academic_year_name = None

    @api.constrains('academic_year_end_date')
    def _check_academic_year_end_date(self):
        for rec in self:
            if rec.academic_year_end_date <= rec.academic_year_start_date:
                raise ValidationError(_("End Date must be greater than Start Date"))

    @api.constrains('academic_year_number_of_semesters')
    def _check_academic_year_number_of_semesters(self):
        for rec in self:
            if rec.academic_year_number_of_semesters < 2:
                raise ValidationError(_("Number of Semesters must be greater than 1"))

    @api.model
    @tools.ormcache()
    def get_semester_name_selection(self):
        def ordinal(n: int):
            return 'th' if 11 <= (n % 100) <= 13 else ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        selection_list = []
        company_id = self.env['res.company'].browse(
            self.env.context.get('allowed_company_ids')[0]
        ) if self.env.context.get('allowed_company_ids') else self.env.company
        for i in range(1, company_id.academic_year_number_of_semesters + 1):
            selection_list.append((f'{i}{ordinal(i)}', _(num2words(i, ordinal=True).capitalize() + ' Semester')))
        return selection_list
