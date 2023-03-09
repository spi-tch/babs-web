import json
import logging
import os
import uuid

from flask import Blueprint, request, redirect
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import services
from constants import GOOGLE_CAL_APP_NAME, GOOGLE_MAIL_APP_NAME, NOTION_APP_NAME
from data_access import find_user_by_uuid
from schema import validate_request, AddApplicationSchema
from util.auth import get_auth_url, get_creds

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "True"
CLIENT_SECRETS_FILE = "client_config.json" if os.getenv("FLASK_CONFIG") == "production" else "client_secret.json"
apps = Blueprint("apps", __name__)

logger = logging.getLogger(__name__)

app_service = services.AppService()
auth_service = services.AuthService()
user_service = services.UserService()


@apps.route(f'/{VERSION}/application', methods=['POST'])
def add_app():
  request_data = request.form
  valid, data = validate_request(request_data, AddApplicationSchema())
  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    auth = request_data['Authorization'].split(' ')[1]
    claims = verify_oauth2_token(auth, requests.Request(),
                                 audience=os.getenv('GOOGLE_CLIENT_ID'))
  except Exception as e:
    logger.error(e)
    message = {"success": False, "message": f"Bad request. {e}"}
    return message, 400

  try:
    if not claims['email_verified']:
      raise Exception('User email has not been verified by Google.')
    __id__ = uuid.uuid5(uuid.NAMESPACE_URL, claims['email'])
    user = find_user_by_uuid(str(__id__))

    if redirect_url := get_auth_url(data["app"], user):
      return redirect(redirect_url, code=303)
    return {'message': 'Invalid request. Could not add application.', 'success': False}, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': 'Unable to add application.'}
    return message, 500


# Get all apps for user
@apps.route(f'/{VERSION}/application', methods=['GET'])
def get_apps():
  try:
    status, message, data = app_service.get_apps(request.environ['user'].uuid)
    if not status:
      response = {'message': message, 'success': False}
      return response, 400
    response = {'message': message, 'success': True, 'data': data}
    return response, 200
  except Exception as e:
    logger.error(e)
    response = {'message': 'Unable to get applications', 'success': False}
    return response, 500


@apps.route(f'/{VERSION}/application', methods=['DELETE'])
def delete_app():
  try:
    application = request.json['application']
    if application == GOOGLE_MAIL_APP_NAME:
      email = request.json["email"]
      status, message = app_service.remove_app(request.environ['user'], application, email)
    elif application == GOOGLE_CAL_APP_NAME:
      status, message = app_service.remove_app(request.environ['user'], application)
    else:
      return {'message': 'Invalid application', 'success': False}, 400
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True}, 200
  except Exception as e:
    logger.error('Unable to delete application', e)
    return {'message': 'Unable to delete application', 'success': False}, 500


@apps.route("/auth_callback")
def auth_callback():
  try:
    creds, user, app_name, claims = get_creds(request.args, request.url)
    if app_name == GOOGLE_MAIL_APP_NAME or app_name == GOOGLE_CAL_APP_NAME:
      auth_service.store_google_creds(user, creds, claims["email"])
      store_apps(app_name, {
        "uuid": user,
        "email": claims["email"]
      }, creds=json.loads(creds.to_json()), email=claims["email"])
    elif app_name == NOTION_APP_NAME:
      auth_service.store_notion_creds(user, creds)
      store_apps(app_name, {
        "uuid": user,
        "email": ""
      }, creds=creds, email="")
    else:
      return {"error": "Invalid Application", "success": False}, 400

    return redirect(f"{os.getenv('FRONTEND_URL')}/app/integrations", 302)
  except Exception as e:
    logger.error(e)
    return {"error": "Something Happened", "success": False}, 500


@apps.route(f"/{VERSION}/application", methods=["PATCH"])
def update_app():
  try:
    app_name = request.json.get("app")
    conf = request.json.get("config")
    status, message = app_service.update_app_conf(request.environ['user'].uuid, app_name, conf)
    if not status:
      return {"message": message, "success": False}, 400
    return {"message": message, "success": True}, 200
  except Exception as e:
    logger.error(e)
    return {"message": "Unable to update application config.", "success": False}, 400


def store_apps(app_name, user: dict, creds: dict, email):
  try:
    creds.pop("expiry", None)
    _, message, data = app_service.add_app(app_name, user, creds, email)
  except Exception as e:
    logger.error(e)
    raise
