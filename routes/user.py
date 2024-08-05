import logging
import os

from flask import Blueprint, request

import services
from schema import validate_request, UserRegistrationSchema, UserUpdateSchema, WaitlistSchema
from services import build_user_object

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

user = Blueprint('user', __name__)

logger = logging.getLogger(__name__)
user_service = services.UserService()


@user.route(f'/user/login', methods=['POST'])
def register_or_login():
  request_data = request.json
  valid, data = validate_request(request_data, UserRegistrationSchema())

  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    status, message, user_info = user_service.login_or_register(data)
    if status:
      message = {'success': True, 'message': message, 'data': user_info}
      return message, 200
    message = {'success': False, 'message': message}
    return message, 400
  except ValueError as e:
    logger.error(e)
    message = {'success': False, 'message': f'{e}'}
    return message, 401
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to register user.'}
    return message, 500


@user.route(f'/user/update', methods=['POST'])
def update_user():
  request_data = request.json
  valid, data = validate_request(request_data, UserUpdateSchema())

  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    status, message, user_info = user_service.update_user(data, request.environ['user'])
    if status:
      message = {'success': True, 'message': message, 'data': user_info}
      return message, 200
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': 'Unable to update user info'}
    return message, 500


@user.route(f'/user', methods=['GET'])
def get_user():
  user_info = request.environ['user']
  try:
    if not user_info:
      message = {'success': True, 'message': 'Unable to find user.'}
      return message, 404

    user_info = build_user_object(user_info)
    message = {"success": True, "message": "Found user", "data": user_info}
    return message, 200

  except Exception as e:
    logger.error(f"Unable to fetch user.", e)
    return {"success": False, "message": "Unable to get user info. Contact admin."}, 500


@user.route(f'/wait', methods=['POST'])
def add_user_to_waitlist():
  request_data = request.json
  valid, data = validate_request(request_data, WaitlistSchema())
  try:
    if not valid:
      message = {'success': False, 'errors': data}
      return message, 400

    if user_service.add_to_waitlist(data['email']):
      message = {"success": True, "message": "email added to waitlist"}
      return message, 200

    # return success even if email addition fails
    message = {"success": True, "message": "email added to waitlist"}
    return message, 200

  except Exception as e:
    logger.error(f"Unable to fetch user.", e)
    return {"success": False, "message": "Unable to add user to waitlist"}, 500
