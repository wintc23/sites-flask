from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message, notify = False):
  response = jsonify({'error': 'bad request', 'message': message, 'notify': notify})
  response.status_code = 400
  return response


def unauthorized(message, notify = False):
  response = jsonify({'error': 'unauthorized', 'message': message, 'notify': notify})
  response.status_code = 401
  return response


def forbidden(message, notify = False):
  response = jsonify({'error': 'forbidden', 'message': message, 'notify': notify})
  response.status_code = 403
  return response

def not_found(message, notify = False):
  response = jsonify({'error': 'not found', 'message': message, 'notify': notify})
  response.status_code = 404
  return response

@api.errorhandler(ValidationError)
def validation_error(e):
  return bad_request(e.args[0])