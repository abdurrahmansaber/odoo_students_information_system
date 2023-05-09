import odoo
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessError


class SisApi(http.Controller):

    @http.route('/sis/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password):
        if not http.db_filter([db]):
            raise AccessError("Database not found.")

        request.session.authenticate(db, login, password)
        request.session.db = db
        registry = odoo.modules.registry.Registry(db)
        with registry.cursor() as cr:
            env = odoo.api.Environment(cr, request.session.uid, request.session.context)
            session_info = env['ir.http'].session_info()
            user_id = request.env['res.users'].browse(request.session.uid)
            return {"session_id": request.httprequest.cookies.get('session_id'),
                    "is_student": user_id.is_student,
                    "uid": request.session.uid}

    @http.route('/sis/user/info', type='json', auth="user")
    def user_info(self, uid: int):
        uid = int(uid)
        user_id = request.env['res.users'].browse(uid)
        return {"name": user_id.name}
