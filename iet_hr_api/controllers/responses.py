from odoo.http import request

def valid_response(message='success', result=None, status=200):
    return request.make_json_response({
        'success': True,
        'message': message,
        'result': result,
    }, status=status)

def invalid_response(message='Failed', result=None, status=400):
    return request.make_json_response({
        'success': False,
        'message': message,
        'result': result,
    }, status=status)
