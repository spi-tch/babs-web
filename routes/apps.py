import json
import logging
import os
from uuid import UUID

import flask
import google_auth_oauthlib.flow
from flask import Blueprint, request, redirect

import services

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"
CLIENT_SECRETS_FILE = "client_secret.json"
apps = Blueprint("apps", __name__)

logger = logging.getLogger(__name__)

app_service = services.AppService()
auth_service = services.AuthService()
user_service = services.UserService()

SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/gmail.modify",
          "https://www.googleapis.com/auth/contacts",
          "openid", "https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/userinfo.profile"]
APP_REDIRECT = ""


@apps.route(f'/{VERSION}/application', methods=['POST'])
def add_app():
  app_name = request.json.get("app", None)
  if not app_name:
    return {'message': 'App name is required', 'success': False}, 400

  state = f"{request.environ['user'].uuid}/{app_name}"
  global APP_REDIRECT
  APP_REDIRECT = f"{request.origin}/app/integrations"
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES)
  flow.redirect_uri = flask.url_for("apps.auth_callback", _external=True, _scheme="http")
  authorization_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    login_hint=request.environ["user"].email,
    prompt="consent", state=state)

  return {"redirect_url": authorization_url}, 200


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
    status, message = app_service.remove_app(request.environ['user'].uuid, request.json['application'])
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True}, 200
  except Exception as e:
    logger.error('Unable to delete application', e)
    return {'message': 'Unable to delete application', 'success': False}, 500


@apps.route("/auth_callback")
def auth_callback():
  try:
    args = request.args
    state = args["state"]
    user = state.split("/")[0]
    email = user_service.find_user(UUID(user)).email
    app_name = state.split("/")[1]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('apps.auth_callback', _external=True, _scheme="http")
    # todo: fix this url
    authorization_response = request.url
    authorization_response = authorization_response.replace("http://", "https://")

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    auth_service.store_google_creds(user, credentials)
    store_apps(app_name, {
      "uuid": user,
      "email": email
    }, creds=json.loads(credentials.to_json()))
    return redirect(APP_REDIRECT, 302)
  except Exception as e:
    logger.error(e)
    return {"error": "Something Happened", "success": False}, 500


def store_apps(app_name, user: dict, creds: dict):
  try:
    _, message, data = app_service.add_app(app_name, user, creds)
  except Exception as e:
    logger.error(e)
    raise
