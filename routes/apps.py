import logging
import os

import flask
import google_auth_oauthlib.flow
from flask import Blueprint, request, jsonify

import services

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"
CLIENT_SECRETS_FILE = "../client_secret.json"
apps = Blueprint("apps", __name__)

logger = logging.getLogger(__name__)
app_service = services.AppService()


@apps.route(f'/{VERSION}/application/<application>', methods=['POST'])
def add_app(application):
  app_name = request.view_args["application"]

  if not app_name:
    return jsonify({'message': 'App name is required', 'success': False}), 400

  try:
    status, message, data = app_service.add_app(app_name, request.environ['user'].uuid)
    if not status:
      response = jsonify({'message': message, 'success': False})
      response.headers.add('Access-Control-Allow-Origin', '*')
      response.headers.add('Access-Control-Allow-Credentials', 'true')
      response.status_code = 400
      return response
    response = jsonify({'message': message, 'success': True, 'data': data})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 200
    return {'message': message, 'success': True, 'data': data}, 200
  except Exception as e:
    logger.error(e)

    response = jsonify({'message': 'Unable to add app', 'success': False})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 500
    return response


# Get all apps for user
@apps.route(f'/{VERSION}/application', methods=['GET'])
def get_apps():
  try:
    status, message, data = app_service.get_apps(request.environ['user'].uuid)
    if not status:
      response = jsonify({'message': message, 'success': False})
      response.headers.add('Access-Control-Allow-Origin', '*')
      response.headers.add('Access-Control-Allow-Credentials', 'true')
      return response, 400
    response = jsonify({'message': message, 'success': True, 'data': data})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 200
    return response
  except Exception as e:
    logger.error(e)
    response = jsonify({'message': 'Unable to get applications', 'success': False})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 500
    return response

@apps.route(f'/{VERSION}/application', methods=['DELETE'])
def delete_app():
  try:
    status, message = app_service.remove_app(request.environ['user'].uuid, request.json['application'])
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True}, 200
  except Exception as e:
    logger.error('Unable to delete application', e)
    return {'message': 'Unable to delete application', 'success': False}, 500
