from odoo import api, fields, models, _
from odoo.exceptions import UserError


@api.model
def _get_level_selection(self):
    return self.company_id.get_level_selection()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    internal_reference = fields.Char(help='unique internal id for students', required=True, tracking=True)
    national_id = fields.Char(tracking=True)

    section_id = fields.Many2one(comodel_name='section', tracking=True)
    academic_program_id = fields.Many2one(comodel_name='academic.program', tracking=True)
    academic_advisor_id = fields.Many2one('hr.employee', tracking=True)
    department_id = fields.Many2one(comodel_name='department', tracking=True)
    archive_line_ids = fields.One2many('student.archive.line', 'partner_id', tracking=True)

    level = fields.Selection(_get_level_selection, required=True,
                             tracking=True)

    state = fields.Selection([('n/a', 'N/A'), ('pass', 'PASS'), ('fail', 'FAIL')], default='n/a',
                             help='technical field used to create student archive records')
    is_student = fields.Boolean(help='technical field used in domain filtering')
    total_grade = fields.Float(help='technical field used to create student archive records')

    @api.onchange('state')
    def _create_student_yearly_archive(self):
        for rec in self:
            if rec.state != 'n/a':
                vals = {
                    'partner_id': rec.id,
                    'academic_year': rec.company_id.academic_year_name,
                    'academic_program_id': rec.academic_program_id.id,
                    'level': rec.level,
                    'state': rec.state,
                    'total_grade': rec.total_grade,
                    'course_ids': rec.course_ids.ids,
                    'section_id': rec.section_id.name,
                    'academic_advisor_id': rec.academic_advisor_id.id,
                }
                self.env['student.archive.line'].create(vals)
                levels = [code for code, name in rec.company_id.get_level_selection()]

                if rec.state == 'pass':
                    if rec.level == levels[len(levels) - 1]:
                        vals = {
                            'student_name': rec.name,
                            'company_id': rec.company_id.name,
                            'student_code': rec.internal_reference,
                            'national_id': rec.national_id,
                            'phone': rec.phone,
                            'email': rec.email,
                            'lang': rec.lang.name,
                            'street': rec.street,
                            'city': rec.city,
                            'state': rec.state_id.name,
                            'country': rec.country_id.name,
                            'line_ids': [(6, 0, rec.archive_line_ids.ids)]
                        }
                        self.env['student.archive'].create(vals)
                    else:
                        rec.level = levels[levels.index(rec.level) + 1]
                rec.state = 'n/a'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res_users_obj = self.env['res.users']
        new_users = []
        for record in res.filtered('is_student'):
            new_users.append({
                'name': record.name,
                'login': record.internal_reference,
                'partner_id': record.id,
                'password': 'changeme',
                'groups_id': [6, 0, self.env['ir.model.data']._xmlid_to_res_id('base.group_portal',
                                                                               raise_if_not_found=False)]
            })
        res_users_obj.create(new_users)

        return res

    @api.constrains('internal_reference')
    def _check_unique_internal_reference(self):
        for rec in self:
            if self.env['res.partner'].search_count(
                    [('internal_reference', '=', rec.internal_reference.strip().replace(' ', '')),
                     ('id', '!=', rec.id)]):
                raise UserError(_('Cannot create students with duplicated internal id'))

    @api.constrains('national_id')
    def _check_unique_national_id(self):
        for rec in self:
            if self.env['res.partner'].search_count(
                    [('national_id', '=', rec.national_id.strip().replace(' ', '')), ('id', '!=', rec.id)]):
                raise UserError(_('Cannot create students with duplicated national id'))
