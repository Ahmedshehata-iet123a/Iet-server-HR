from odoo import http
from odoo.http import request
from .responses import valid_response, invalid_response
import json
import ast
from odoo.addons.mobikul_odoo_attendance.controllers.main import MobikulAttendanceAPI


class HRApi(MobikulAttendanceAPI):

    def _get_authenticated_user(self):
        auth_res = self._MobikulAttendanceAPI__auth(authorize=True)
        if not auth_res.get('success'):
            return None, invalid_response(
                message=auth_res.get('message', 'Unauthorized access. Invalid or missing token.'),
                status=401
            )

        user = auth_res.get('context', {}).get('user')
        if not user:
            return None, invalid_response(message="User context not found.", status=401)

        return user, None

    @http.route('/v2/mobikul/odoo_attendance/profile', type='http', auth="none", methods=['GET'])
    def profile(self):
        response = super(HRApi, self).profile()

        response_data = json.loads(response.data.decode('utf-8'))

        if response_data.get('success'):
            user, error_resp = self._get_authenticated_user()
            if not error_resp and user and user.employee_id:
                employee = user.employee_id.sudo()

                extra_data = {
                    "number_of_tickets": employee.contract_id.number_of_tickets if employee.contract_id else 0,
                    "leave_days_balance": getattr(employee, 'leave_days_balance', 0.0),
                    "leave_days_taken": getattr(employee, 'leave_days_taken', 0.0),
                    "leave_net_days": getattr(employee, 'net_days', 0.0),
                    "leave_days_policy": getattr(employee, 'leave_policy', ""),
                }

                if 'employeeDetails' in response_data:
                    response_data['employeeDetails'].update(extra_data)
                else:
                    response_data['employeeDetails'] = extra_data

        return self._response('Profile', response_data)

    @http.route("/api/hr.leave.type/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_time_off_types(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            lang_code = kwargs.get('lang')
            leave_type_env = request.env['hr.leave.type'].with_user(user.id)

            if lang_code:
                leave_type_env = leave_type_env.with_context(lang=lang_code)

            hr_leave_types = leave_type_env.search([])

            if not hr_leave_types:
                return invalid_response(message='Leave Types Not Found', status=200)

            result = []
            for leave_type in hr_leave_types:
                result.append({
                    'id': leave_type.id,
                    'name': leave_type.name,
                    'support_document': leave_type.support_document,
                    'requires_allocation': leave_type.requires_allocation,
                    'request_unit': leave_type.request_unit,
                })

            return valid_response(
                message=f"Leave Types data has been successfully retrieved. Total Leave Types: {len(result)}",
                result=result)

        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.leave/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_time_off(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            hr_leaves = request.env['hr.leave'].with_user(user.id).search(domain)
            if not hr_leaves:
                return invalid_response(message='Leaves Not Found', status=200)
            result = []
            for leave in hr_leaves:
                result.append({
                    'id': leave.id,
                    'private_name': leave.private_name,
                    'holiday_status_id': {
                        'id': leave.holiday_status_id.id,
                        'name': leave.holiday_status_id.name,
                    },
                    'attachment_ids': [
                        {
                            'id': attachment.id,
                            'name': attachment.name,
                        } for attachment in leave.attachment_ids
                    ],
                    'state': leave.state,
                    'request_unit_half': leave.request_unit_half,
                    'request_unit_hours': leave.request_unit_hours,
                    'date_period': leave.request_date_from_period,
                    'request_date_from': leave.request_date_from,
                    'request_date_to': leave.request_date_to,
                    'request_hour_from': leave.request_hour_from,
                    'request_hour_to': leave.request_hour_to,
                    'duration_display': leave.duration_display,
                    'notes': leave.notes,
                    'number_of_days': int(leave.number_of_days),
                })

            return valid_response(
                message=f"Leaves data has been successfully retrieved. Total Leaves: {len(result)}",
                result=result)

        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/time_off/employee/<int:employee_id>", type="http", methods=["GET"], auth="public", csrf=False)
    def get_employee_time_off(self, employee_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            employee = request.env['hr.employee'].with_user(user.id).browse(employee_id)
            if not employee.exists():
                return invalid_response(message="Employee Not Found.", status=200)

            hr_leaves = request.env['hr.leave'].with_user(user.id).search([('employee_id', '=', employee_id)])

            if not hr_leaves:
                return invalid_response(message=f'No Leaves Found for Employee ID: {employee_id}', status=200)

            result = []
            for leave in hr_leaves:
                result.append({
                    'id': leave.id,
                    'private_name': leave.private_name,
                    'holiday_status_id': {
                        'id': leave.holiday_status_id.id,
                        'name': leave.holiday_status_id.name,
                    },
                    'attachment_ids': [
                        {
                            'id': attachment.id,
                            'name': attachment.name,
                        } for attachment in leave.attachment_ids
                    ],
                    'state': leave.state,
                    'request_unit_half': leave.request_unit_half,
                    'request_unit_hours': leave.request_unit_hours,
                    'date_period': leave.request_date_from_period,
                    'request_date_from': leave.request_date_from,
                    'request_date_to': leave.request_date_to,
                    'request_hour_from': leave.request_hour_from,
                    'request_hour_to': leave.request_hour_to,
                    'duration_display': leave.duration_display,
                    'notes': leave.notes,
                    'number_of_days': int(leave.number_of_days),
                })

            return valid_response(
                message=f"Leaves data for Employee ID {employee_id} has been successfully retrieved. Total Leaves: {len(result)}",
                result=result)

        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.leave/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_time_off(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['holiday_status_id', 'request_date_from', 'request_date_to', 'employee_id']):
                return invalid_response(message="Missing required fields for time off creation.", status=400)

            employee_id = request.env['hr.employee'].with_user(user.id).browse(int(vals.get('employee_id')))
            if not employee_id.exists():
                return invalid_response(message="Invalid Employee ID.", status=404)

            leave_type = request.env['hr.leave.type'].with_user(user.id).browse(int(vals.get('holiday_status_id')))
            if not leave_type.exists():
                return invalid_response(message="Invalid Leave Type ID.", status=404)

            hr_leave = request.env['hr.leave'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Time Off request created successfully. ID: {hr_leave.id}",
                result={'create_id': hr_leave.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.leave/<int:leave_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_time_off(self, leave_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            hr_leave = request.env['hr.leave'].with_user(user.id).browse(leave_id)
            if not hr_leave.exists():
                return invalid_response(message="Time Off record not found.", status=200)

            if hr_leave.state not in ['confirm', 'validate1', 'cancel']:
                return invalid_response(
                    message=f"Cannot delete time off in state: {hr_leave.state}.",
                    status=403)

            request.env.cr.execute("DELETE FROM hr_leave WHERE id = %s", (leave_id,))
            request.env.cr.commit()
            return valid_response(message=f"Time Off record with ID {leave_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.leave/<int:leave_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_time_off(self, leave_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            hr_leave = request.env['hr.leave'].with_user(user.id).browse(leave_id)
            if not hr_leave.exists():
                return invalid_response(message="Time Off record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            hr_leave.write(vals)
            return valid_response(
                message=f"Time Off record with ID {leave_id} updated successfully.",
                result={'write_id': hr_leave.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.leave.allocation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_time_off_types_allocation(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            lang_code = kwargs.get('lang')
            domain = []

            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []

            allocation_env = request.env['hr.leave.allocation'].with_user(user.id)

            if lang_code:
                allocation_env = allocation_env.with_context(lang=lang_code)

            hr_leave_allocations = allocation_env.search(domain)

            if not hr_leave_allocations:
                return invalid_response(message='Leave Allocations Not Found', status=200)

            result = []
            for allocation in hr_leave_allocations:
                result.append({
                    'id': allocation.id,
                    'name': allocation.name,
                    'employee_id': {
                        'id': allocation.employee_id.id,
                        'name': allocation.employee_id.name,
                    },
                    'holiday_status_id': {
                        'id': allocation.holiday_status_id.id,
                        'name': allocation.holiday_status_id.name,
                    },
                    'allocation_type': allocation.allocation_type,
                    'duration_display': allocation.number_of_days,
                    'state': allocation.state,
                })

            return valid_response(
                message=f"Leave Allocations data has been successfully retrieved. Total Allocations: {len(result)}",
                result=result)

        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ir.attachment/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_attachment(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['name']):
                return invalid_response(message="Missing required fields for attachment creation.", status=400)

            attachment = request.env['ir.attachment'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Attachment created successfully. ID: {attachment.id}",
                result={'create_id': attachment.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ir.attachment/<int:attachment_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_attachment(self, attachment_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            attachment = request.env['ir.attachment'].with_user(user.id).browse(attachment_id)
            if not attachment.exists():
                return invalid_response(message="Attachment not found.", status=404)

            attachment.unlink()
            return valid_response(message=f"Attachment with ID {attachment_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/loans.creation/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_loan(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['employee_id', 'amount']):
                return invalid_response(message="Missing required fields for loan creation.", status=400)

            loan = request.env['loans'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Loan created successfully. ID: {loan.id}",
                result={'create_id': loan.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/loans.creation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_loan(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            loans = request.env['loans'].with_user(user.id).search(domain)
            if not loans:
                return invalid_response(message='Loans Not Found', status=200)
            result = []
            for loan in loans:
                result.append({
                    'id': loan.id,
                    'name': loan.name,
                    'date': loan.date.strftime('%Y-%m-%d') if loan.date else None,
                    'deduction_date': loan.deduction_date.strftime('%Y-%m-%d') if loan.deduction_date else None,
                    'amount': loan.amount,
                    'no_of_installment': loan.no_of_installment,
                    'loans_monthly_amount': loan.amount / loan.no_of_installment if loan.no_of_installment > 0 else 0,
                    'state': loan.state,
                })
            return valid_response(
                message=f"Loans data has been successfully retrieved. Total Loans: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/loans.creation/<int:loan_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_loan(self, loan_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            loan = request.env['loans'].with_user(user.id).browse(loan_id)
            if not loan.exists():
                return invalid_response(message="Loan record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            loan.write(vals)
            return valid_response(
                message=f"Loan record with ID {loan_id} updated successfully.",
                result={'write_id': loan.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/loans.creation/<int:loan_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_loan(self, loan_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            loan = request.env['loans'].with_user(user.id).browse(loan_id)
            if not loan.exists():
                return invalid_response(message="Loan record not found.", status=404)

            loan.unlink()
            return valid_response(message=f"Loan with ID {loan_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/salary.advance/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_salary_advance(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['employee_id', 'amount']):
                return invalid_response(message="Missing required fields for loan creation.", status=400)

            salary_advance = request.env['salary.advance'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Salary Advance created successfully. ID: {salary_advance.id}",
                result={'create_id': salary_advance.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/salary.advance/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_salary_advance(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            salary_advances = request.env['salary.advance'].with_user(user.id).search(domain)
            if not salary_advances:
                return invalid_response(message='Salary Advance Not Found', status=200)
            result = []
            for salary_advance in salary_advances:
                result.append({
                    'id': salary_advance.id,
                    'name': salary_advance.name,
                    'date': salary_advance.date.strftime('%Y-%m-%d') if salary_advance.date else None,
                    'deduction_date': salary_advance.deduction_date.strftime(
                        '%Y-%m-%d') if salary_advance.deduction_date else None,
                    'amount': salary_advance.amount,
                    'reason': salary_advance.reason,
                    'state': salary_advance.state,
                })
            return valid_response(
                message=f"Salary Advance data has been successfully retrieved. Total Loans: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/salary.advance/<int:salary_advance_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_salary_advance(self, salary_advance_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            salary_advance = request.env['salary.advance'].with_user(user.id).browse(salary_advance_id)
            if not salary_advance.exists():
                return invalid_response(message="Salary Advance record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            salary_advance.write(vals)
            return valid_response(
                message=f"Salary Advance record with ID {salary_advance_id} updated successfully.",
                result={'write_id': salary_advance.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/salary.advance/<int:loan_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_salary_advance(self, loan_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            loan = request.env['salary.advance'].with_user(user.id).browse(loan_id)
            if not loan.exists():
                return invalid_response(message="salary advance record not found.", status=404)

            loan.unlink()
            return valid_response(message=f"salary advance with ID {loan_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ticket.request/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_ticket(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id', 'flight_date', 'trip_type', 'flight_ticket_cost', 'number_of_tickets']):
                return invalid_response(message="Missing required fields for ticket creation.", status=400)
            employee = request.env['hr.employee'].with_user(user.id).search([('id', '=', int(vals['employee_id']))])
            contract_number_of_tickets = 0
            if employee.contract_id and employee.contract_id.number_of_tickets:
                contract_number_of_tickets = employee.contract_id.number_of_tickets
            if int(vals['number_of_tickets']) > contract_number_of_tickets:
                return invalid_response(
                    message="The Number Of Tickets Must Be Less Than Or Equal Number Of Tickets In Contract.",
                    status=400)
            ticket = request.env['flight.tickets'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Ticket created successfully. ID: {ticket.id}",
                result={'create_id': ticket.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ticket.request/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_ticket(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            tickets = request.env['flight.tickets'].with_user(user.id).search(domain)
            if not tickets:
                return invalid_response(message='Tickets Not Found', status=200)
            result = []
            for ticket in tickets:
                result.append({
                    'id': ticket.id,
                    'employee_id': {
                        'id': ticket.employee_id.id,
                        'name': ticket.employee_id.name,
                    },
                    'flight_date': ticket.flight_date.strftime('%Y-%m-%d') if ticket.flight_date else None,
                    'trip_type': ticket.trip_type,
                    'visa_period': ticket.visa_period,
                    'number_of_tickets': ticket.number_of_tickets,
                    'flight_ticket_cost': ticket.flight_ticket_cost,
                    'booked_by': ticket.booked_by,
                    'flight_for': ticket.flight_for,
                    'initial_flight_type': ticket.initial_flight_type,
                    'departure_airport': ticket.departure_airport,
                    'state': ticket.state,
                })
            return valid_response(
                message=f"Tickets data has been successfully retrieved. Total Tickets: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ticket.request/<int:ticket_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_ticket(self, ticket_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            ticket = request.env['flight.tickets'].with_user(user.id).browse(ticket_id)
            if not ticket.exists():
                return invalid_response(message="Ticket record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            ticket.write(vals)
            return valid_response(
                message=f"Ticket record with ID {ticket_id} updated successfully.",
                result={'write_id': ticket.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ticket.request/<int:ticket_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_ticket(self, ticket_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            ticket = request.env['flight.tickets'].with_user(user.id).browse(ticket_id)
            if not ticket.exists():
                return invalid_response(message="Ticket record not found.", status=404)
            ticket.unlink()
            return valid_response(message=f"Ticket with ID {ticket_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.departure.reason/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_departure_reasons(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            departure_reasons = request.env['hr.departure.reason'].with_user(user.id).search([])
            if not departure_reasons:
                return invalid_response(message='Departure Reasons Not Found', status=200)
            result = []
            for departure_reason in departure_reasons:
                result.append({
                    'id': departure_reason.id,
                    'name': departure_reason.name,
                })
            return valid_response(
                message=f"Departure Reasons data has been successfully retrieved. Total Departure Reasons: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.resignation/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_resignation(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['employee_id', 'hr_departure_id']):
                return invalid_response(message="Missing required fields for resignation creation.", status=400)

            employee_id = request.env['hr.employee'].with_user(user.id).browse(int(vals.get('employee_id')))
            if not employee_id.exists():
                return invalid_response(message="Invalid Employee ID.", status=400)

            resignation = request.env['resignation.request'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Resignation created successfully. ID: {resignation.id}",
                result={'create_id': resignation.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.resignation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_resignation(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            resignations = request.env['resignation.request'].with_user(user.id).search(domain)
            if not resignations:
                return invalid_response(message='Resignations Not Found', status=200)
            result = []
            for resignation in resignations:
                result.append({
                    'id': resignation.id,
                    'company_id': resignation.company_id.id,
                    'employee_id': {
                        'id': resignation.employee_id.id,
                        'name': resignation.employee_id.name,
                    },
                    'hr_departure_id': {
                        'id': resignation.hr_departure_id.id,
                        'name': resignation.hr_departure_id.name,
                    },
                    'departure_reason': resignation.departure_reason,
                    'contract_date_end': resignation.contract_date_end.strftime(
                        '%Y-%m-%d') if resignation.contract_date_end else None,
                    'state': resignation.state,
                })
            return valid_response(
                message=f"Resignations data has been successfully retrieved. Total Resignations: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.resignation/<int:resignation_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_resignation(self, resignation_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            resignation = request.env['resignation.request'].with_user(user.id).browse(resignation_id)
            if not resignation.exists():
                return invalid_response(message="Resignation record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            resignation.write(vals)
            return valid_response(
                message=f"Resignation record with ID {resignation_id} updated successfully.",
                result={'write_id': resignation.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.resignation/<int:resignation_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_resignation(self, resignation_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            resignation = request.env['resignation.request'].with_user(user.id).browse(resignation_id)
            if not resignation.exists():
                return invalid_response(message="Resignation record not found.", status=404)
            resignation.unlink()
            return valid_response(message=f"Resignation with ID {resignation_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/return.vacation/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_return_vacation(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['employee_id']):
                return invalid_response(message="Missing required fields for Return Vacation creation.", status=400)

            new_record = request.env['return.vacation'].with_user(user.id).create(vals)
            return valid_response(
                message=f"Return From Vacation record created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/return.vacation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_return_vacation(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['return.vacation'].with_user(user.id).search(domain)
            if not records:
                return invalid_response(message='No Return From Vacation records found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'state': getattr(rec, 'state', None),
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'leave_id': rec.leave_id.id if hasattr(rec, 'leave_id') and rec.leave_id else None,
                    'return_date': rec.return_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                   'return_date') and rec.return_date else None,
                    'description': getattr(rec, 'description', None),
                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/return.vacation/<int:record_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_return_vacation(self, record_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            record = request.env['return.vacation'].with_user(user.id).browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            record.write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/return.vacation/<int:record_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_return_vacation(self, record_id, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            record = request.env['return.vacation'].with_user(user.id).browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.payslip/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_employee_payslips(self, **kwargs):
        try:
            user, error_resp = self._get_authenticated_user()
            if error_resp: return error_resp

            employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            if not employee:
                return invalid_response(message="No employee linked to the current user.", status=404)

            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            domain.append(('employee_id', '=', employee.id))

            payslips = request.env['hr.payslip'].with_user(user.id).search(domain)

            if not payslips:
                return invalid_response(message='No Payslips Found', status=200)

            result = []
            for slip in payslips:
                result.append({
                    'id': slip.id,
                    'reference': getattr(slip, 'number', None) or getattr(slip, 'name', None),
                    'employee_id': slip.employee_id.id if slip.employee_id else None,
                    'employee_name': slip.employee_id.name if slip.employee_id else None,
                    'batch_id': slip.payslip_run_id.id if hasattr(slip,
                                                                  'payslip_run_id') and slip.payslip_run_id else None,
                    'batch_name': slip.payslip_run_id.name if hasattr(slip,
                                                                      'payslip_run_id') and slip.payslip_run_id else None,
                    'date_from': slip.date_from.strftime('%Y-%m-%d') if hasattr(slip,
                                                                                'date_from') and slip.date_from else None,
                    'date_to': slip.date_to.strftime('%Y-%m-%d') if hasattr(slip, 'date_to') and slip.date_to else None,
                    'basic_wage': getattr(slip, 'basic_wage', 0.0),
                    'gross_wage': getattr(slip, 'gross_wage', 0.0),
                    'net_wage': getattr(slip, 'net_wage', 0.0),
                    'state': getattr(slip, 'state', None),
                })

            return valid_response(
                message=f"Payslips retrieved successfully. Total Records: {len(result)}",
                result=result)

        except Exception as error:
            return invalid_response(message=str(error), status=500)