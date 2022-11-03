import logging
import os

import flask
import google_auth_oauthlib.flow
from flask import Blueprint, request

import services

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"
CLIENT_SECRETS_FILE = "/Users/temi/PycharmProjects/babs-app/client_secret_378035869959" \
                      "-d31h5fconbohk5i19ud81le0gn3kiapg.apps.googleusercontent.com-6.json"
auth = Blueprint("auth", __name__)

logger = logging.getLogger(__name__)
auth_service = services.AuthService()


@auth.route(f"/{VERSION}/auth", methods=["POST", "GET"])
def authorize():
  # data = request.json
  flask.session["user"] = "my_user"
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, scopes=["https://www.googleapis.com/auth/calendar"]
  )

  flow.redirect_uri = flask.url_for("auth.auth_callback", _external=True)
  authorization_url, state = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true"
  )

  flask.session["state"] = state

  return flask.redirect(authorization_url)


@auth.route(f"/auth_callback")
def auth_callback():
  try:
    state = flask.session["state"]
    user = flask.session["user"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=["https://www.googleapis.com/auth/calendar"], state=state
    )
    flow.redirect_uri = flask.url_for('auth.auth_callback', _external=True)
    authorization_response = flask.request.url

    # todo: This requires SSL
    flow.fetch_token(authorization_response=authorization_response)

    # todo: store in DB
    credentials = flow.credentials
    auth_service.store_google_creds(user, credentials)
    return {"message": "User successfully authorized", "success": " True"}, 200
  except Exception as e:
    logger.error(e)
    return {"error": "Something Happened", "success": False}, 500
