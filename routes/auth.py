import logging
import os

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

SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/gmail.modify",
          "https://www.googleapis.com/auth/contacts",
          "openid", "https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/userinfo.profile"]


@auth.route(f"/{VERSION}/auth", methods=["GET"])
def authorize():
  try:
    data = request.json
  except Exception as e:
    data = {"scopes": SCOPES}
  state = f"{request.environ['user'].uuid}"
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=data["scopes"])
  flow.redirect_uri = flask.url_for("auth.auth_callback", _external=True, _scheme="https")
  authorization_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    login_hint=request.environ["user"].email,
    prompt="consent", state=state)

  return {"redirect_url": authorization_url}, 200


@auth.route("/auth_callback")
def auth_callback():
  try:
    args = request.args
    user = args["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=user)
    flow.redirect_uri = flask.url_for('auth.auth_callback', _external=True, _scheme="https")
    # todo: fix this url
    authorization_response = flask.url_for("auth.auth", _external=True, _scheme="https")
    authorization_response += f"?state={user}"

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    auth_service.store_google_creds(user, credentials)
    return {"message": "User successfully authorized", "success": " True"}, 200
  except Exception as e:
    logger.error(e)
    return {"error": "Something Happened", "success": False}, 500
