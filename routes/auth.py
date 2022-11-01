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


@auth.route(f"/", methods=["GET"])
def begin():
  return (
      '<table>' +
      '<tr><td><a href="/test">Test an API request</a></td>' +
      '<td>Submit an API request and see a formatted JSON response. ' +
      '    Go through the authorization flow if there are no stored ' +
      '    credentials for the user.</td></tr>' +
      '<tr><td><a href="/v0/auth">Test the auth flow directly</a></td>' +
      '<td>Go directly to the authorization flow. If there are stored ' +
      '    credentials, you still might not be prompted to reauthorize ' +
      '    the application.</td></tr>' +
      '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
      '<td>Revoke the access token associated with the current user ' +
      '    session. After revoking credentials, if you go to the test ' +
      '    page, you should see an <code>invalid_grant</code> error.' +
      '</td></tr>' +
      '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
      '<td>Clear the access token currently stored in the user session. ' +
      '    After clearing the token, if you <a href="/test">test the ' +
      '    API request</a> again, you should go back to the auth flow.' +
      '</td></tr></table>'
  )


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
