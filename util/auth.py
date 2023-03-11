import logging
import os

import flask
import google_auth_oauthlib.flow
import requests
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token

from constants import (
  NOTION_APP_NAME, GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME, GMAIL_SCOPES, CALENDAR_SCOPES,
  BASE_SCOPES
)

CLIENT_SECRETS_FILE = "client_config.json" if os.getenv("FLASK_CONFIG") == "production" else "client_secret.json"
logger = logging.getLogger(__name__)


def get_auth_url(app, user):
  if app == NOTION_APP_NAME:
    return os.getenv("NOTION_AUTH_URL") + f"&state={user.uuid}/{app}"
  elif app == GOOGLE_MAIL_APP_NAME:
    scopes = GMAIL_SCOPES + BASE_SCOPES
  elif app == GOOGLE_CAL_APP_NAME:
    scopes = CALENDAR_SCOPES + BASE_SCOPES
  else:
    return None

  try:
    state = f"{user.uuid}/{app}"
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=scopes)
    flow.redirect_uri = flask.url_for("apps.auth_callback", _external=True, _scheme="http")
    authorization_url, state = flow.authorization_url(
      access_type="offline",
      include_granted_scopes="true",
      prompt="consent", state=state)
    return authorization_url
  except Exception as e:
    logger.error(e)
    return None


def get_creds(args, url=None):
  state = args["state"]
  user = state.split("/")[0]
  app_name = state.split("/")[1]

  if app_name == NOTION_APP_NAME:
    code = args["code"]
    # requests.post(, data={"code": code, "state": state})
    response = requests.post("https://api.notion.com/v1/oauth/token",
                             json={"code": code,
                                   "grant_type": "authorization_code",
                                   "redirect_uri": f"{os.getenv('BASE_URL')}/auth_callback"},
                             auth=(os.getenv("NOTION_CLIENT_ID"), os.getenv("NOTION_CLIENT_SECRET"))
                             )
    creds = response.json()
    return creds, user, app_name, None
  elif app_name == GOOGLE_MAIL_APP_NAME or app_name == GOOGLE_CAL_APP_NAME:
    scopes = args["scope"].split(" ")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=scopes, state=state)
    flow.redirect_uri = flask.url_for('apps.auth_callback', _external=True, _scheme="http")
    authorization_response = url
    # authorization_response = authorization_response.replace("http://", "https://")

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    claims = verify_oauth2_token(credentials.id_token, Request(), audience=os.getenv('GOOGLE_CLIENT_ID'))
    return credentials, user, app_name, claims
