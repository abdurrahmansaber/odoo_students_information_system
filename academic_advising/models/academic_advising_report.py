from odoo import api, fields, models


class AcademicAdvisingReport(models.Model):
    _name = 'academic.advising.report'
    _description = 'Academic Advising Report'
    _inherit = 'mail.thread'
    _rec_name = 'academic_advisor_id'
    _order = 'company_id, academic_advisor_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', readonly=True,
                                 default=lambda self: self.env.company)
    academic_advisor_id = fields.Many2one('hr.employee', required=True)

    count_excellent_grade = fields.Integer(required=True, string='No. of Excellent Grade Students', default=0)
    percentage_excellent_grade = fields.Float(string='Percentage', compute='_compute_percentage_excellent_grade')
    count_very_good_grade = fields.Integer(required=True, string='No. of Very Good Grade Students', default=0)
    percentage_very_good_grade = fields.Float(string='Percentage', compute='_compute_percentage_very_good_grade')
    count_good_grade = fields.Integer(required=True, string='No. of Good Grade Students', default=0)
    percentage_good_grade = fields.Float(string='Percentage', compute='_compute_percentage_good_grade')
    count_pass_grade = fields.Integer(required=True, string='No. of Pass Grade Students', default=0)
    percentage_pass_grade = fields.Float(string='Percentage', compute='_compute_percentage_pass_grade')
    count_pass_with_subjects_grade = fields.Integer(required=True, string='No. of Pass with Subject(s) Grade Students',
                                                    default=0)
    percentage_pass_with_subjects_grade = fields.Float(string='Percentage',
                                                       compute='_compute_percentage_pass_with_subjects_grade')
    count_failed = fields.Integer(required=True, string='No. of Failed Students', default=0)
    percentage_failed = fields.Float(string='Percentage', compute='_compute_percentage_failed')
    count_academic_warning = fields.Integer(required=True, string='No. of Students who Received an Academic Warning',
                                            default=0)
    percentage_academic_warning = fields.Float(string='Percentage', compute='_compute_percentage_academic_warning')

    action_towards_talented_students = fields.Text(translate=True)
    action_towards_talented_students_result = fields.Text(string='Result', translate=True)
    action_towards_valedictorians = fields.Text(translate=True)
    action_towards_valedictorians_result = fields.Text(string='Result', translate=True)
    action_towards_faltered_students = fields.Text(translate=True)
    action_towards_faltered_students_result = fields.Text(string='Result', translate=True)
    action_towards_disabled_students = fields.Text(translate=True)
    action_towards_disabled_students_result = fields.Text(string='Result', translate=True)

    constraints = fields.Text(translate=True)
    suggestions = fields.Text(translate=True)
    notes = fields.Text(translate=True)

    @api.depends('count_excellent_grade')
    def _compute_percentage_excellent_grade(self):
        for rec in self:
            rec.percentage_excellent_grade = rec.count_excellent_grade / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0

    @api.depends('count_very_good_grade')
    def _compute_percentage_very_good_grade(self):
        for rec in self:
            rec.percentage_very_good_grade = rec.count_very_good_grade / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0

    @api.depends('count_good_grade')
    def _compute_percentage_good_grade(self):
        for rec in self:
            rec.percentage_good_grade = rec.count_good_grade / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0

    @api.depends('count_pass_grade')
    def _compute_percentage_pass_grade(self):
        for rec in self:
            rec.percentage_pass_grade = rec.count_pass_grade / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0

    @api.depends('count_pass_with_subjects_grade')
    def _compute_percentage_pass_with_subjects_grade(self):
        for rec in self:
            rec.percentage_pass_with_subjects_grade = rec.count_pass_with_subjects_grade / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0

    @api.depends('count_failed')
    def _compute_percentage_failed(self):
        for rec in self:
            rec.percentage_failed = rec.count_failed / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0

    @api.depends('count_academic_warning')
    def _compute_percentage_academic_warning(self):
        for rec in self:
            rec.percentage_academic_warning = rec.count_academic_warning / len(
                rec.academic_advisor_id.academic_advisee_ids
            ) if rec.academic_advisor_id.academic_advisee_ids else 0
