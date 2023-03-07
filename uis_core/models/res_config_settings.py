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
