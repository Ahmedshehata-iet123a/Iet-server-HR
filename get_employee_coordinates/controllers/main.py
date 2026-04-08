# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http


class GetEmployeeCoordinatesController(http.Controller):
    @http.route('/get_coordinates', type="json", auth="public")
    def get_coordinates(self, employee_id):
        if isinstance(employee_id, (list, tuple)):
            employee_id = employee_id[0]
        employee_id = int(employee_id)

        Coordinate = request.env['hr.employee.coordinate'].sudo()
        data = Coordinate.search_read(
            [('employee_ids', 'in', [employee_id])],
            fields=['name', 'latitude', 'longitude', 'distance']
        )
        return data or []
