import ast
import logging
import os
import uuid

import flask
import google_auth_oauthlib.flow
from flask import Blueprint, request

import services

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"
CLIENT_SECRETS_FILE = "client_secret.json"
auth = Blueprint("auth", __name__)

logger = logging.getLogger(__name__)
auth_service = services.AuthService()
user_service = services.UserService()


@auth.route(f"/{VERSION}/auth", methods=["GET"])
def authorize():
  try:
    data = request.json
  except Exception as e:
    logger.error(e)
    data = {"scopes": ["https://www.googleapis.com/auth/calendar",
                       "https://www.googleapis.com/auth/gmail.modify",
                       "https://www.googleapis.com/auth/contacts",
                       "openid", "https://www.googleapis.com/auth/userinfo.email",
                       "https://www.googleapis.com/auth/userinfo.profile"]}
  state = f"{request.environ['user'].uuid} {data['scopes']}"
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=data["scopes"], state=state)
  flow.redirect_uri = flask.url_for("auth.auth_callback", _external=True, _scheme="https")
  authorization_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    login_hint=request.environ["user"].email,
    prompt="consent")

  return {"authorization_url": authorization_url}


@auth.route(f"/auth_callback")
def auth_callback():
  try:
    args = request.args
    state = args["state"].split(" ", maxsplit=1)
    user = state[0]
    scopes = ast.literal_eval(state[1])

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=scopes, state=args["state"])
    flow.redirect_uri = flask.url_for('auth.auth_callback', _external=True, _scheme="https")
    authorization_response = flask.request.url

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    auth_service.store_google_creds(user, credentials)
    return {"message": "User successfully authorized", "success": " True"}, 200
  except Exception as e:
    logger.error(e)
    return {"error": "Something Happened", "success": False}, 500
