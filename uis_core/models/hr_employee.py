from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection(selection_add=[('teacher', 'Teacher')], ondelete={'teacher': 'set default'})

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res_users_obj = self.env['res.users']

        for record in res.filtered(lambda emp: emp.employee_type == 'teacher'):
            vals = {
                'name': record.name,
                'login': record.work_email,
                'password': 'changeme',
                'groups_id': [6, 0, self.env['ir.model.data']._xmlid_to_res_id('base.group_user',
                                                                               raise_if_not_found=False)]
            }
            user_id = res_users_obj.create(vals)
            user_id.partner_id.is_teacher = True
            user_id.partner_id.company_id = record.company_id
            record.user_id = user_id
            record.work_email = user_id.login
            record.address_home_id = record.user_id.partner_id
        return res


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # inheriting field name from hr.employee.base to enable translating name in hr.employee
    # because it's a related field
    name = fields.Char(translate=True)
