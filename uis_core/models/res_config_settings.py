from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Company setup
    academic_year_name = fields.Char(related='company_id.academic_year_name', string='Name')
    academic_year_code = fields.Char(related='company_id.academic_year_code', string='Code', readonly=False)
    academic_year_start_date = fields.Date(related='company_id.academic_year_start_date', string='Start Date',
                                           readonly=False)
    academic_year_end_date = fields.Date(related='company_id.academic_year_end_date', string='End Date', readonly=False)
    academic_year_number_of_semesters = fields.Integer(related='company_id.academic_year_number_of_semesters',
                                                       string='No. of Semesters', readonly=False)
    minimum_subject_passing_percentage = fields.Float(related='company_id.minimum_subject_passing_percentage',
                                                      help='The minimum percentage that a student have to accumulate to'
                                                           'pass the subject, This criteria applies for all faculty '
                                                           'subjects.', readonly=False)
    maximum_failed_subjects = fields.Integer(related='company_id.maximum_failed_subjects',
                                             help='The maximum number of subjects that a student can fail and still '
                                                  'be moved to the next level', readonly=False)
