from odoo import http
from odoo.http import request
from .responses import valid_response, invalid_response
import json
import ast


class HRServiceApi(http.Controller):

    # ==========================================================================
    # Model: request.maintenance.devices.printers
    # ==========================================================================

    @http.route("/api/request.maintenance.devices.printers/create", type="http", methods=["POST"], auth="public",
                csrf=False)
    def create_request_maintenance_printers(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.maintenance.devices.printers'].sudo().create(vals)
            return valid_response(
                message=f"Printer Maintenance Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.maintenance.devices.printers/search", type="http", methods=["GET"], auth="public",
                csrf=False)
    def get_request_maintenance_printers(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.maintenance.devices.printers'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Printer Maintenance Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.maintenance.devices.printers/<int:record_id>", type="http", methods=["PUT"],
                auth="public", csrf=False)
    def update_request_maintenance_printers(self, record_id, **kwargs):
        try:
            record = request.env['request.maintenance.devices.printers'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.maintenance.devices.printers/<int:record_id>", type="http", methods=["DELETE"],
                auth="public", csrf=False)
    def delete_request_maintenance_printers(self, record_id, **kwargs):
        try:
            record = request.env['request.maintenance.devices.printers'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: request.office.supplies
    # ==========================================================================

    @http.route("/api/request.office.supplies/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_request_office_supplies(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.office.supplies'].sudo().create(vals)
            return valid_response(
                message=f"Office Supplies Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.office.supplies/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_request_office_supplies(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.office.supplies'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Office Supplies Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.office.supplies/<int:record_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_request_office_supplies(self, record_id, **kwargs):
        try:
            record = request.env['request.office.supplies'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.office.supplies/<int:record_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_request_office_supplies(self, record_id, **kwargs):
        try:
            record = request.env['request.office.supplies'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: request.plumbing.and.electrical
    # ==========================================================================

    @http.route("/api/request.plumbing.and.electrical/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_request_plumbing_electrical(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.plumbing.and.electrical'].sudo().create(vals)
            return valid_response(
                message=f"Plumbing and Electrical Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.plumbing.and.electrical/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_request_plumbing_electrical(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.plumbing.and.electrical'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Plumbing and Electrical Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.plumbing.and.electrical/<int:record_id>", type="http", methods=["PUT"], auth="public",
                csrf=False)
    def update_request_plumbing_electrical(self, record_id, **kwargs):
        try:
            record = request.env['request.plumbing.and.electrical'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.plumbing.and.electrical/<int:record_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_request_plumbing_electrical(self, record_id, **kwargs):
        try:
            record = request.env['request.plumbing.and.electrical'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: request.change.salary.account
    # ==========================================================================

    @http.route("/api/bank.account/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_bank_account(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['res.partner.bank'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Bank Account Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'acc_number': getattr(rec, 'acc_number', None),
                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.change.salary.account/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_request_change_salary_account(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.change.salary.account'].sudo().create(vals)
            return valid_response(
                message=f"Change Salary Account Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.change.salary.account/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_request_change_salary_account(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.change.salary.account'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Change Salary Account Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'new_request_no': rec.new_request_no.id if hasattr(rec,
                                                                       'new_request_no') and rec.new_request_no else None,
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.change.salary.account/<int:record_id>", type="http", methods=["PUT"], auth="public",
                csrf=False)
    def update_request_change_salary_account(self, record_id, **kwargs):
        try:
            record = request.env['request.change.salary.account'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.change.salary.account/<int:record_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_request_change_salary_account(self, record_id, **kwargs):
        try:
            record = request.env['request.change.salary.account'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: request.document.transaction
    # ==========================================================================

    @http.route("/api/location/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_locations(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['location'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Location Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'name': getattr(rec, 'name', None),
                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.document.transaction/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_request_document_transaction(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.document.transaction'].sudo().create(vals)
            return valid_response(
                message=f"Document Transaction Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.document.transaction/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_request_document_transaction(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.document.transaction'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Document Transaction Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_to': getattr(rec, 'request_to', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.document.transaction/<int:record_id>", type="http", methods=["PUT"], auth="public",
                csrf=False)
    def update_request_document_transaction(self, record_id, **kwargs):
        try:
            record = request.env['request.document.transaction'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.document.transaction/<int:record_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_request_document_transaction(self, record_id, **kwargs):
        try:
            record = request.env['request.document.transaction'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: request.specify.letter
    # ==========================================================================

    @http.route("/api/request.specify.letter/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_request_specify_letter(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.specify.letter'].sudo().create(vals)
            return valid_response(
                message=f"Specify Letter Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.specify.letter/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_request_specify_letter(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.specify.letter'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Specify Letter Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.specify.letter/<int:record_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_request_specify_letter(self, record_id, **kwargs):
        try:
            record = request.env['request.specify.letter'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.specify.letter/<int:record_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_request_specify_letter(self, record_id, **kwargs):
        try:
            record = request.env['request.specify.letter'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: request.transfer.employee
    # ==========================================================================

    @http.route("/api/request.transfer.employee/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_request_transfer_employee(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['request.transfer.employee'].sudo().create(vals)
            return valid_response(
                message=f"Employee Transfer Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.transfer.employee/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_request_transfer_employee(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['request.transfer.employee'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Employee Transfer Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'new_branch': rec.new_branch.id if hasattr(rec, 'new_branch') and rec.new_branch else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.transfer.employee/<int:record_id>", type="http", methods=["PUT"], auth="public",
                csrf=False)
    def update_request_transfer_employee(self, record_id, **kwargs):
        try:
            record = request.env['request.transfer.employee'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/request.transfer.employee/<int:record_id>", type="http", methods=["DELETE"], auth="public",
                csrf=False)
    def delete_request_transfer_employee(self, record_id, **kwargs):
        try:
            record = request.env['request.transfer.employee'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # Model: others
    # ==========================================================================

    @http.route("/api/others/create", type="http", methods=["POST"], auth="public", csrf=False)
    def create_others(self, **kwargs):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not all(k in vals.keys() for k in
                       ['employee_id']):
                return invalid_response(message="Missing required employee_id required field creation.", status=400)
            new_record = request.env['others'].sudo().create(vals)
            return valid_response(
                message=f"Other Request created successfully. ID: {new_record.id}",
                result={'create_id': new_record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/others/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_others(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))
            records = request.env['others'].sudo().search(domain)
            if not records:
                return invalid_response(message='No Other Requests found.', status=200)

            result = []
            for rec in records:
                result.append({
                    'id': rec.id,
                    'employee_id': rec.employee_id.id if hasattr(rec, 'employee_id') and rec.employee_id else None,
                    'name': getattr(rec, 'name', None),
                    'state': getattr(rec, 'state', None),
                    'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                     'request_date') and rec.request_date else None,

                })
            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(result)}",
                result=result)
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/others/<int:record_id>", type="http", methods=["PUT"], auth="public", csrf=False)
    def update_others(self, record_id, **kwargs):
        try:
            record = request.env['others'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            record.sudo().write(vals)
            return valid_response(
                message=f"Record with ID {record_id} updated successfully.",
                result={'write_id': record.id}
            )
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    @http.route("/api/others/<int:record_id>", type="http", methods=["DELETE"], auth="public", csrf=False)
    def delete_others(self, record_id, **kwargs):
        try:
            record = request.env['others'].sudo().browse(record_id)
            if not record.exists():
                return invalid_response(message="Record not found.", status=404)

            record.sudo().unlink()
            return valid_response(message=f"Record with ID {record_id} deleted successfully.")
        except Exception as error:
            return invalid_response(message=str(error), status=500)

    # ==========================================================================
    # All HR Services
    # ==========================================================================

    @http.route("/api/hr_services/search", type="http", methods=["GET"], auth="public", csrf=False)
    def get_all_hr_services_requests(self, **kwargs):
        try:
            domain = ast.literal_eval(kwargs.get('domain', '[]'))

            hr_service_models = [
                'request.maintenance.devices.printers',
                'request.office.supplies',
                'request.plumbing.and.electrical',
                'request.change.salary.account',
                'request.document.transaction',
                'request.specify.letter',
                'request.transfer.employee',
                'others',
            ]

            all_results = []

            for model_name in hr_service_models:
                records = request.env[model_name].sudo().search(domain)
                for rec in records:
                    record_data = {
                        'id': rec.id,
                        'service_type': model_name,
                        'employee_id': rec.employee_id.id if hasattr(rec,
                                                                     'employee_id') and rec.employee_id else None,
                        'employee_name': rec.employee_id.name if hasattr(rec,
                                                                         'employee_id') and rec.employee_id else None,
                        'name': getattr(rec, 'name', None),
                        'state': getattr(rec, 'state', None),
                        'request_date': rec.request_date.strftime('%Y-%m-%d') if hasattr(rec,
                                                                                         'request_date') and rec.request_date else None,
                        'new_request_no': rec.new_request_no.id if hasattr(rec,
                                                                           'new_request_no') and rec.new_request_no else None,
                        'new_branch': rec.new_branch.id if hasattr(rec, 'new_branch') and rec.new_branch else None,
                        'request_to': getattr(rec, 'request_to', None),

                    }
                    all_results.append(record_data)
                    # if model_name == 'request.change.salary.account':
                    #     all_results.append({
                    #         'new_request_no': rec.new_request_no.id if hasattr(rec,
                    #                                                            'new_request_no') and rec.new_request_no else None,
                    #     })
                    # if model_name == 'request.transfer.employee':
                    #     all_results.append({
                    #         'new_branch': rec.new_branch.id if hasattr(rec, 'new_branch') and rec.new_branch else None,
                    #
                    #     })
                    # if model_name == 'request.document.transaction':
                    #     all_results.append({
                    #         'request_to': getattr(rec, 'request_to', None),
                    #
                    #     })

            if not all_results:
                return invalid_response(message='No HR Service Requests found.', status=200)

            return valid_response(
                message=f"Data retrieved successfully. Total Records: {len(all_results)}",
                result=all_results)
        except Exception as error:
            return invalid_response(message=str(error), status=500)
