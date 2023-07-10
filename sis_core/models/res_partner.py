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
