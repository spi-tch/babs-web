import json
import logging
import os

import flask
import google_auth_oauthlib.flow
from flask import Blueprint, request, redirect
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import services
from constants import GOOGLE_CAL_APP_NAME, GOOGLE_MAIL_APP_NAME, GMAIL_SCOPES, CALENDAR_SCOPES, BASE_SCOPES

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
  app_name = request.json.get("app", None)
  if not app_name:
    return {'message': 'App name is required', 'success': False}, 400

  if app_name == GOOGLE_MAIL_APP_NAME:
    scopes = GMAIL_SCOPES + BASE_SCOPES
  elif app_name == GOOGLE_CAL_APP_NAME:
    scopes = CALENDAR_SCOPES + BASE_SCOPES
  else:
    return {'message': 'App name is invalid', 'success': False}, 400

  state = f"{request.environ['user'].uuid}/{app_name}"
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=scopes)
  flow.redirect_uri = flask.url_for("apps.auth_callback", _external=True, _scheme="https")
  authorization_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    # login_hint=request.environ["user"].email,
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
    args = request.args
    state = args["state"]
    user = state.split("/")[0]
    app_name = state.split("/")[1]

    scopes = args["scope"].split(" ")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=scopes, state=state)
    flow.redirect_uri = flask.url_for('apps.auth_callback', _external=True, _scheme="http")
    # todo: fix this url
    authorization_response = request.url
    # authorization_response = authorization_response.replace("http://", "https://")

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    claims = verify_oauth2_token(credentials.id_token, requests.Request(), audience=os.getenv('GOOGLE_CLIENT_ID'))
    auth_service.store_google_creds(user, credentials, claims["email"])
    store_apps(app_name, {
      "uuid": user,
      "email": claims["email"]
    }, creds=json.loads(credentials.to_json()), email=claims["email"])
    return redirect(f"{os.getenv('FRONTEND_URL')}/app/integrations", 302)
  except Exception as e:
    logger.error(e)
    return {"error": "Something Happened", "success": False}, 500


def store_apps(app_name, user: dict, creds: dict, email):
  try:
    creds.pop("expiry", None)
    _, message, data = app_service.add_app(app_name, user, creds, email)
  except Exception as e:
    logger.error(e)
    raise
