# -*- coding: utf-8 -*-
from odoo import http


class ResignationRequest(http.Controller):
    @http.route('/resignation_request/resignation_request', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/resignation_request/resignation_request/objects', auth='public')
    def list(self, **kw):
        return http.request.render('resignation_request.listing', {
            'root': '/resignation_request/resignation_request',
            'objects': http.request.env['resignation_request.resignation_request'].search([]),
        })

    @http.route('/resignation_request/resignation_request/objects/<model("resignation_request.resignation_request"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('resignation_request.object', {
            'object': obj
        })
