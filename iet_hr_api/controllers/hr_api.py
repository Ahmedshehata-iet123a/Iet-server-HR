from odoo import http
from odoo.http import request
from .responses import valid_response, invalid_response
import json
import ast


class HRApi(http.Controller):
    @http.route("/api/hr.leave.type/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_time_off_types(self, **kwargs):
        try:
            hr_leave_types = request.env['hr.leave.type'].sudo().search([])
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
            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            hr_leaves = request.env['hr.leave'].sudo().search(domain)
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

    #### **Get Time Off for a Specific Employee (`/api/time_off/employee/<id>`)**
    @http.route("/api/time_off/employee/<int:employee_id>", type="http", methods=["GET"], auth="public", csrf=False)
    def get_employee_time_off(self, employee_id, **kwargs):
        try:
            # Check if the employee exists
            employee = request.env['hr.employee'].sudo().browse(employee_id)
            if not employee.exists():
                return invalid_response(message="Employee Not Found.", status=200)

            # Search for leaves related to the specific employee
            hr_leaves = request.env['hr.leave'].sudo().search([('employee_id', '=', employee_id)])

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

    #### **Create Time Off Request (`/api/hr.leave/create`)**
    @http.route("/api/hr.leave/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_time_off(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['holiday_status_id', 'request_date_from', 'request_date_to', 'employee_id']):
                return invalid_response(message="Missing required fields for time off creation.", status=400)
            # Ensure employee_id is a valid ID
            employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
            if not employee_id.exists():
                return invalid_response(message="Invalid Employee ID.", status=404)
            # Ensure holiday_status_id is a valid ID
            leave_type = request.env['hr.leave.type'].sudo().browse(int(vals.get('holiday_status_id')))
            if not leave_type.exists():
                return invalid_response(message="Invalid Leave Type ID.", status=404)

            hr_leave = request.env['hr.leave'].sudo().create(vals)
            return valid_response(
                message=f"Time Off request created successfully. ID: {hr_leave.id}",
                result={'create_id': hr_leave.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # DELETE: Already HTTP, no change needed
    @http.route("/api/hr.leave/<int:leave_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_time_off(self, leave_id, **kwargs):
        try:
            hr_leave = request.env['hr.leave'].sudo().browse(leave_id)
            if not hr_leave.exists():
                return invalid_response(message="Time Off record not found.", status=200)

            if hr_leave.state not in ['confirm', 'validate1', 'cancel']:
                return invalid_response(
                    message=f"Cannot delete time off in state: {hr_leave.state}.",
                    status=403)
            # Unlink directly without triggering the ondelete logic
            request.env.cr.execute("DELETE FROM hr_leave WHERE id = %s", (leave_id,))
            request.env.cr.commit()
            return valid_response(message=f"Time Off record with ID {leave_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    #### **Update Time Off Request (`/api/hr.leave/<id>`)**
    @http.route("/api/hr.leave/<int:leave_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_time_off(self, leave_id, **kwargs):
        try:
            hr_leave = request.env['hr.leave'].sudo().browse(leave_id)
            if not hr_leave.exists():
                return invalid_response(message="Time Off record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            hr_leave.sudo().write(vals)
            return valid_response(
                message=f"Time Off record with ID {leave_id} updated successfully.",
                result={'write_id': hr_leave.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.leave.allocation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_time_off_types_allocation(self, **kwargs):
        try:
            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            hr_leave_allocations = request.env['hr.leave.allocation'].sudo().search(domain)
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

    # Attachments
    @http.route("/api/ir.attachment/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_attachment(self, **kwargs):
        try:
            all_attachment = request.env['ir.attachment'].sudo().search([])
            print(len(all_attachment))
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['name']):
                return invalid_response(message="Missing required fields for attachment creation.", status=400)

            attachment = request.env['ir.attachment'].sudo().create(vals)
            return valid_response(
                message=f"Attachment created successfully. ID: {attachment.id}",
                result={'create_id': attachment.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ir.attachment/<int:attachment_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_attachment(self, attachment_id, **kwargs):
        try:
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            if not attachment.exists():
                return invalid_response(message="Attachment not found.", status=404)

            attachment.sudo().unlink()
            return valid_response(message=f"Attachment with ID {attachment_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # Loans
    @http.route("/api/loans.creation/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_loan(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id', 'amount']):
                return invalid_response(message="Missing required fields for loan creation.", status=400)

            loan = request.env['loans'].sudo().create(vals)
            return valid_response(
                message=f"Loan created successfully. ID: {loan.id}",
                result={'create_id': loan.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/loans.creation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_loan(self, **kwargs):
        try:
            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            loans = request.env['loans'].sudo().search(domain)
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
            loan = request.env['loans'].sudo().browse(loan_id)
            if not loan.exists():
                return invalid_response(message="Loan record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            loan.sudo().write(vals)
            return valid_response(
                message=f"Loan record with ID {loan_id} updated successfully.",
                result={'write_id': loan.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/loans.creation/<int:loan_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_loan(self, loan_id, **kwargs):
        try:
            loan = request.env['loans'].sudo().browse(loan_id)
            if not loan.exists():
                return invalid_response(message="Loan record not found.", status=404)

            # Unlink using ORM (triggers ondelete hooks if any)
            loan.sudo().unlink()
            return valid_response(message=f"Loan with ID {loan_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # Salary Advance
    @http.route("/api/salary.advance/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_salary_advance(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id', 'amount']):
                return invalid_response(message="Missing required fields for loan creation.", status=400)

            salary_advance = request.env['salary.advance'].sudo().create(vals)
            return valid_response(
                message=f"Salary Advance created successfully. ID: {salary_advance.id}",
                result={'create_id': salary_advance.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/salary.advance/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_salary_advance(self, **kwargs):
        try:
            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            salary_advances = request.env['salary.advance'].sudo().search(domain)
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
            salary_advance = request.env['salary.advance'].sudo().browse(salary_advance_id)
            if not salary_advance.exists():
                return invalid_response(message="Salary Advance record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            salary_advance.sudo().write(vals)
            return valid_response(
                message=f"Salary Advance record with ID {salary_advance_id} updated successfully.",
                result={'write_id': salary_advance.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/salary.advance/<int:salary_advance_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_salary_advance(self, loan_id, **kwargs):
        try:
            loan = request.env['salary.advance'].sudo().browse(loan_id)
            if not loan.exists():
                return invalid_response(message="salary advance record not found.", status=404)

            # Unlink using ORM (triggers ondelete hooks if any)
            loan.sudo().unlink()
            return valid_response(message=f"salary advance with ID {loan_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # Ticket
    @http.route("/api/ticket.request/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_ticket(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id', 'flight_date', 'trip_type', 'flight_ticket_cost', 'number_of_tickets']):
                return invalid_response(message="Missing required fields for ticket creation.", status=400)
            employee = request.env['hr.employee'].sudo().search([('id', '=', int(vals['employee_id']))])
            contract_number_of_tickets = 0
            if employee.contract_id and employee.contract_id.number_of_tickets:
                contract_number_of_tickets = employee.contract_id.number_of_tickets
            if int(vals['number_of_tickets']) > contract_number_of_tickets:
                return invalid_response(
                    message="The Number Of Tickets Must Be Less Than Or Equal Number Of Tickets In Contract.",
                    status=400)
            ticket = request.env['flight.tickets'].sudo().create(vals)
            return valid_response(
                message=f"Ticket created successfully. ID: {ticket.id}",
                result={'create_id': ticket.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ticket.request/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_ticket(self, **kwargs):
        try:
            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            tickets = request.env['flight.tickets'].sudo().search(domain)
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
            ticket = request.env['flight.tickets'].sudo().browse(ticket_id)
            if not ticket.exists():
                return invalid_response(message="Ticket record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            ticket.sudo().write(vals)
            return valid_response(
                message=f"Ticket record with ID {ticket_id} updated successfully.",
                result={'write_id': ticket.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/ticket.request/<int:ticket_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_ticket(self, ticket_id, **kwargs):
        try:
            ticket = request.env['flight.tickets'].sudo().browse(ticket_id)
            if not ticket.exists():
                return invalid_response(message="Ticket record not found.", status=404)
            ticket.sudo().unlink()
            return valid_response(message=f"Ticket with ID {ticket_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # Resignation
    @http.route("/api/hr.departure.reason/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_departure_reasons(self, **kwargs):
        try:
            departure_reasons = request.env['hr.departure.reason'].sudo().search([])
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
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in ['employee_id', 'hr_departure_id']):
                return invalid_response(message="Missing required fields for resignation creation.", status=400)

            # Ensure employee_id is a valid ID
            employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
            if not employee_id.exists():
                return invalid_response(message="Invalid Employee ID.", status=400)

            resignation = request.env['resignation.request'].sudo().create(vals)
            return valid_response(
                message=f"Resignation created successfully. ID: {resignation.id}",
                result={'create_id': resignation.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.resignation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_resignation(self, **kwargs):
        try:
            domain = []
            if kwargs.get('domain'):
                domain = ast.literal_eval(kwargs.get('domain')) or []
            resignations = request.env['resignation.request'].sudo().search(domain)
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
            resignation = request.env['resignation.request'].sudo().browse(resignation_id)
            if not resignation.exists():
                return invalid_response(message="Resignation record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            resignation.sudo().write(vals)
            return valid_response(
                message=f"Resignation record with ID {resignation_id} updated successfully.",
                result={'write_id': resignation.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/hr.resignation/<int:resignation_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_resignation(self, resignation_id, **kwargs):
        try:
            resignation = request.env['resignation.request'].sudo().browse(resignation_id)
            if not resignation.exists():
                return invalid_response(message="Resignation record not found.", status=404)
            resignation.sudo().unlink()
            return valid_response(message=f"Resignation with ID {resignation_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: return.vacation
    # ==========================================================================

    @http.route("/api/return.vacation/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_return_vacation(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required fields for Return Vacation creation.", status=400)

            new_record = request.env['return.vacation'].sudo().create(vals)
            return valid_response(
                message=f"Return From Vacation record created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/return.vacation/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_return_vacation(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['return.vacation'].sudo().search(domain)
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
            record = request.env['return.vacation'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals:
                return invalid_response(message="No data provided for update.", status=400)

            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/return.vacation/<int:record_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_return_vacation(self, record_id, **kwargs):
        try:
            record = request.env['return.vacation'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # # Employee Trip
    # @http.route("/api/business.trip/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_employee_trip(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['date_from', 'date_to', 'employee_id']):
    #             return invalid_response(message="Missing required fields for employee trip creation.", status=400)
    #
    #         # Ensure employee_id is a valid ID
    #         employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
    #         if not employee_id.exists():
    #             return invalid_response(message="Invalid Employee ID.", status=400)
    #
    #         employee_trip = request.env['business.trip'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Employee Trip created successfully. ID: {employee_trip.id}",
    #             result={'create_id': employee_trip.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/business.trip/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_employee_trip(self, **kwargs):
    #     try:
    #         employee_trips = request.env['business.trip'].sudo().search([])
    #         if not employee_trips:
    #             return invalid_response(message='Employee Trips Not Found', status=404)
    #         result = []
    #         for trip in employee_trips:
    #             result.append({
    #                 'id': trip.id,
    #                 'date': trip.date.strftime('%Y-%m-%d') if trip.date else None,
    #                 'need_ticket': trip.need_ticket,
    #                 'ticket_amount': trip.ticket_amount,
    #                 'need_hotel': trip.need_hotel,
    #                 'hotel_amount': trip.hotel_amount,
    #                 'transport_allow': trip.transport_allow,
    #                 'other_amount': trip.other_amount,
    #                 'trip_dist': [{'id': dest.id, 'name': dest.name} for dest in trip.trip_dist],
    #                 'date_from': trip.date_from.strftime('%Y-%m-%d') if trip.date_from else None,
    #                 'date_to': trip.date_to.strftime('%Y-%m-%d') if trip.date_to else None,
    #                 'days_value': trip.days_value,
    #                 'days_count': trip.days_count,
    #                 'state': trip.state,
    #             })
    #         return valid_response(
    #             message=f"Employee Trips data has been successfully retrieved. Total Trips: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/business.trip/<int:trip_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    # def update_employee_trip(self, trip_id, **kwargs):
    #     try:
    #         employee_trip = request.env['business.trip'].sudo().browse(trip_id)
    #         if not employee_trip.exists():
    #             return invalid_response(message="Employee Trip record not found.", status=404)
    #
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not vals:
    #             return invalid_response(message="No data provided for update.", status=400)
    #
    #         employee_trip.sudo().write(vals)
    #         return valid_response(
    #             message=f"Employee Trip record with ID {trip_id} updated successfully.",
    #             result={'write_id': employee_trip.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/trip.destination/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_trip_destination(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['name']):
    #             return invalid_response(message="Missing required fields for trip destination creation.", status=400)
    #
    #         trip_destination = request.env['trip.destination'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Trip Destination created successfully. ID: {trip_destination.id}",
    #             result={'create_id': trip_destination.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/trip.destination/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_trip_destination(self, **kwargs):
    #     try:
    #         trip_destinations = request.env['trip.destination'].sudo().search([])
    #         if not trip_destinations:
    #             return invalid_response(message='Trip Destinations Not Found', status=404)
    #         result = []
    #         for destination in trip_destinations:
    #             result.append({
    #                 'id': destination.id,
    #                 'name': destination.name,
    #             })
    #         return valid_response(
    #             message=f"Trip Destinations data has been successfully retrieved. Total Destinations: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # # Custody
    # @http.route("/api/custody.request/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_custody(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['date', 'employee_id']):
    #             return invalid_response(message="Missing required fields for custody creation.", status=400)
    #
    #         # Ensure employee_id is a valid ID
    #         employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
    #         if not employee_id.exists():
    #             return invalid_response(message="Invalid Employee ID.", status=400)
    #
    #         custody = request.env['custody.request'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Custody Request created successfully. ID: {custody.id}",
    #             result={'create_id': custody.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/custody.request/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_custody(self, **kwargs):
    #     try:
    #         custodies = request.env['custody.request'].sudo().search([])
    #         if not custodies:
    #             return invalid_response(message='Custody Requests Not Found', status=404)
    #         result = []
    #         for custody in custodies:
    #             result.append({
    #                 'id': custody.id,
    #                 'date': custody.date.strftime('%Y-%m-%d') if custody.date else None,
    #                 'item_id': [{'id': item.id, 'name': item.name} for item in custody.item_id],
    #                 'notes': custody.notes,
    #                 'state': custody.state,
    #             })
    #         return valid_response(
    #             message=f"Custody Requests data has been successfully retrieved. Total Custody Requests: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/custody.request/<int:custody_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    # def update_custody(self, custody_id, **kwargs):
    #     try:
    #         custody = request.env['custody.request'].sudo().browse(custody_id)
    #         if not custody.exists():
    #             return invalid_response(message="Custody record not found.", status=404)
    #
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not vals:
    #             return invalid_response(message="No data provided for update.", status=400)
    #
    #         custody.sudo().write(vals)
    #         return valid_response(
    #             message=f"Custody record with ID {custody_id} updated successfully.",
    #             result={'write_id': custody.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/custody.items/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_custody_item(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['name']):
    #             return invalid_response(message="Missing required fields for custody item creation.", status=400)
    #
    #         custody_item = request.env['custody.items'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Custody Item created successfully. ID: {custody_item.id}",
    #             result={'create_id': custody_item.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/custody.items/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_custody_items(self, **kwargs):
    #     try:
    #         custody_items = request.env['custody.items'].sudo().search([])
    #         if not custody_items:
    #             return invalid_response(message='Custody Items Not Found', status=404)
    #         result = []
    #         for item in custody_items:
    #             result.append({
    #                 'id': item.id,
    #                 'name': item.name,
    #                 'active': item.active,
    #                 'state': item.state,
    #             })
    #         return valid_response(
    #             message=f"Custody Items data has been successfully retrieved. Total Custody Items: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)

    # # Employee Letter
    # @http.route("/api/employee.letter/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_employee_letter(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['date', 'directed_to', 'subject', 'type', 'employee_id']):
    #             return invalid_response(message="Missing required fields for employee letter creation.", status=400)
    #
    #         # Ensure employee_id is a valid ID
    #         employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
    #         if not employee_id.exists():
    #             return invalid_response(message="Invalid Employee ID.", status=400)
    #
    #         employee_letter = request.env['employee.letter'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Employee Letter created successfully. ID: {employee_letter.id}",
    #             result={'create_id': employee_letter.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/employee.letter/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_employee_letter(self, **kwargs):
    #     try:
    #         employee_letters = request.env['employee.letter'].sudo().search([])
    #         if not employee_letters:
    #             return invalid_response(message='Employee Letters Not Found', status=404)
    #         result = []
    #         for letter in employee_letters:
    #             result.append({
    #                 'id': letter.id,
    #                 'date': letter.date.strftime('%Y-%m-%d') if letter.date else None,
    #                 'directed_to': letter.directed_to,
    #                 'subject': letter.subject,
    #                 'type': letter.type,
    #                 'state': letter.state,
    #             })
    #         return valid_response(
    #             message=f"Employee Letters data has been successfully retrieved. Total Letters: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/employee.letter/<int:letter_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    # def update_employee_letter(self, letter_id, **kwargs):
    #     try:
    #         employee_letter = request.env['employee.letter'].sudo().browse(letter_id)
    #         if not employee_letter.exists():
    #             return invalid_response(message="Employee Letter record not found.", status=404)
    #
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not vals:
    #             return invalid_response(message="No data provided for update.", status=400)
    #
    #         employee_letter.sudo().write(vals)
    #         return valid_response(
    #             message=f"Employee Letter record with ID {letter_id} updated successfully.",
    #             result={'write_id': employee_letter.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # # Labor Fees
    # @http.route("/api/labor.fees.request/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_labor_fees(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['labor_fees_type_id', 'request_date', 'amount', 'employee_id']):
    #             return invalid_response(message="Missing required fields for labor fees creation.", status=400)
    #
    #         # Ensure employee_id is a valid ID
    #         employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
    #         if not employee_id.exists():
    #             return invalid_response(message="Invalid Employee ID.", status=400)
    #
    #         labor_fees = request.env['labor.fees.request'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Labor Fees Request created successfully. ID: {labor_fees.id}",
    #             result={'create_id': labor_fees.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/labor.fees.request/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_labor_fees(self, **kwargs):
    #     try:
    #         labor_fees_requests = request.env['labor.fees.request'].sudo().search([])
    #         if not labor_fees_requests:
    #             return invalid_response(message='Labor Fees Requests Not Found', status=404)
    #         result = []
    #         for fees_request in labor_fees_requests:
    #             result.append({
    #                 'id': fees_request.id,
    #                 'labor_fees_type_id': [{'id': fee_type.id, 'name': fee_type.name} for fee_type in
    #                                        fees_request.labor_fees_type_id],
    #                 'request_date': fees_request.request_date.strftime(
    #                     '%Y-%m-%d') if fees_request.request_date else None,
    #                 'description': fees_request.description,
    #                 'current_ex_date': fees_request.current_ex_date.strftime(
    #                     '%Y-%m-%d') if fees_request.current_ex_date else None,
    #                 'renew_ex_date': fees_request.renew_ex_date.strftime(
    #                     '%Y-%m-%d') if fees_request.renew_ex_date else None,
    #                 'amount': fees_request.amount,
    #                 'state': fees_request.state,
    #             })
    #         return valid_response(
    #             message=f"Labor Fees Requests data has been successfully retrieved. Total Requests: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/labor.fees.request/<int:labor_fees_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    # def update_labor_fees(self, labor_fees_id, **kwargs):
    #     try:
    #         labor_fees = request.env['labor.fees.request'].sudo().browse(labor_fees_id)
    #         if not labor_fees.exists():
    #             return invalid_response(message="Labor Fees record not found.", status=404)
    #
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not vals:
    #             return invalid_response(message="No data provided for update.", status=400)
    #
    #         labor_fees.sudo().write(vals)
    #         return valid_response(
    #             message=f"Labor Fees record with ID {labor_fees_id} updated successfully.",
    #             result={'write_id': labor_fees.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/labor.fees.type/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_labor_fees_types(self, **kwargs):
    #     try:
    #         labor_fees_types = request.env['labor.fees.type'].sudo().search([])
    #         if not labor_fees_types:
    #             return invalid_response(message='Labor Fees Types Not Found', status=404)
    #         result = []
    #         for fee_type in labor_fees_types:
    #             result.append({
    #                 'id': fee_type.id,
    #                 'name': fee_type.name,
    #                 'active': fee_type.active,
    #             })
    #         return valid_response(
    #             message=f"Labor Fees Types data has been successfully retrieved. Total Types: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # # Salary Advance
    # @http.route("/api/salary.advance/create", type="http", methods=["POST"], auth="public", csrf=False)
    # def create_salary_advance(self, **kwargs):
    #     try:
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not all(k in vals.keys() for k in ['date', 'employee_id']):
    #             return invalid_response(message="Missing required fields for salary advance creation.", status=400)
    #
    #         # Ensure employee_id is a valid ID
    #         employee_id = request.env['hr.employee'].sudo().browse(int(vals.get('employee_id')))
    #         if not employee_id.exists():
    #             return invalid_response(message="Invalid Employee ID.", status=400)
    #
    #         salary_advance = request.env['salary.advance'].sudo().create(vals)
    #         return valid_response(
    #             message=f"Salary Advance created successfully. ID: {salary_advance.id}",
    #             result={'create_id': salary_advance.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/salary.advance/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_salary_advance(self, **kwargs):
    #     try:
    #         salary_advances = request.env['salary.advance'].sudo().search([])
    #         if not salary_advances:
    #             return invalid_response(message='Salary Advance records Not Found', status=404)
    #         result = []
    #         for advance in salary_advances:
    #             result.append({
    #                 'id': advance.id,
    #                 'leave_id': [{'id': leave.id, 'name': leave.name} for leave in advance.leave_id],
    #                 'date': advance.date.strftime('%Y-%m-%d') if advance.date else None,
    #                 'state': advance.state,
    #             })
    #         return valid_response(
    #             message=f"Salary Advance data has been successfully retrieved. Total Records: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # @http.route("/api/salary.advance/<int:advance_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    # def update_salary_advance(self, advance_id, **kwargs):
    #     try:
    #         salary_advance = request.env['salary.advance'].sudo().browse(advance_id)
    #         if not salary_advance.exists():
    #             return invalid_response(message="Salary Advance record not found.", status=404)
    #
    #         args = request.httprequest.data.decode()
    #         vals = json.loads(args)
    #         if not vals:
    #             return invalid_response(message="No data provided for update.", status=400)
    #
    #         salary_advance.sudo().write(vals)
    #         return valid_response(
    #             message=f"Salary Advance record with ID {advance_id} updated successfully.",
    #             result={'write_id': salary_advance.id}
    #         )
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
    #
    # # Geofences
    # @http.route("/api/hr.attendance.geofence/search", type="http", methods=["GET"], auth="public", csrf=False)
    # def get_geofences(self, **kwargs):
    #     try:
    #         geofences = request.env['hr.attendance.geofence'].sudo().search([])
    #         if not geofences:
    #             return invalid_response(message='Geofences Not Found', status=404)
    #         result = []
    #         for geofence in geofences:
    #             result.append({
    #                 'id': geofence.id,
    #                 'name': geofence.name,
    #                 'description': geofence.description,
    #                 'company_id': [{'id': company.id, 'name': company.name} for company in geofence.company_id],
    #                 'employee_ids': [{'id': employee.id, 'name': employee.name} for employee in geofence.employee_ids],
    #                 'overlay_paths': json.loads(geofence.overlay_paths) if geofence.overlay_paths else {},
    #                 'create_uid': [{'id': user.id, 'name': user.name} for user in geofence.create_uid],
    #                 'create_date': geofence.create_date.strftime(
    #                     '%Y-%m-%dT%H:%M:%SZ') if geofence.create_date else None,
    #                 'write_uid': [{'id': user.id, 'name': user.name} for user in geofence.write_uid],
    #                 'write_date': geofence.write_date.strftime('%Y-%m-%dT%H:%M:%SZ') if geofence.write_date else None,
    #             })
    #         return valid_response(
    #             message=f"Geofences data has been successfully retrieved. Total Geofences: {len(result)}",
    #             result=result)
    #     except Exception as error:
    #         return invalid_response(message=str(error), status=500)
