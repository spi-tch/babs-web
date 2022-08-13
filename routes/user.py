import os

from flask import Blueprint, request

from exceptions import DuplicateUserException
from schema import UserVerificationSchema, validate_request, UserRegistrationSchema
import services

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

register = Blueprint('register', __name__)
verify = Blueprint('verify', __name__)

user_service = services.UserService()


@register.route(f'/{VERSION}/user/register', methods=['POST'])
def register_user():
  request_data = request.json
  valid, data = validate_request(request_data, UserRegistrationSchema())

  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    status, message, user_info = user_service.create_user(data)
    if status:
      message = {'success': True, 'message': message, 'data': user_info}
      return message, 200
    message = {'success': False, 'message': message}
    return message, 400
  except DuplicateUserException as d:
    message = {'success': False, 'message': f'{d}'}
    return message, 400
  except Exception as e:
    message = {'success': False, 'message': f'Unable to register user.'}
    return message, 500


@verify.route(f'/{VERSION}/user/verify', methods=['POST'])
def verify_user():
  request_data = request.json
  valid, data = validate_request(request_data, UserVerificationSchema())

  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    status, message = user_service.verify_user(data)
    if status:
      message = {'success': True, 'message': message}
      return message, 200
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    message = {'success': False, 'message': 'Unable to verify user'}
    print(e)
    return message, 500
