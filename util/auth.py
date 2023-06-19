import logging
import os

import flask
import google_auth_oauthlib.flow
import requests
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
import sqlalchemy as db
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore

from constants import (
    NOTION_APP_NAME, GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME, GMAIL_SCOPES, CALENDAR_SCOPES,
    BASE_SCOPES
)

CLIENT_SECRETS_FILE = "client_config.json" if os.getenv("FLASK_CONFIG") == "production" else "client_secret.json"
logger = logging.getLogger(__name__)

BABS_DB_URL = f"{os.getenv('DB_SCHEME')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}" \
              f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
print(f"DB URI: {BABS_DB_URL}")
engine = db.create_engine(BABS_DB_URL,
                          pool_size=3,
                          pool_pre_ping=True,
                          pool_recycle=1000,
                          max_overflow=0)
metadata = db.MetaData()
state_store = SQLAlchemyOAuthStateStore(expiration_seconds=80, engine=engine)
state_store.metadata = metadata
state_store.metadata.create_all(state_store.engine, tables=[state_store.oauth_states])
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=os.getenv("SLACK_CLIENT_ID"),
    scopes=["channels:read", "groups:read", "chat:write", "app_mentions:read", "im:history", "users:read"],
)


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
        flow.redirect_uri = flask.url_for("apps.auth_callback", _external=True, _scheme="https")
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
                                       "redirect_uri": flask.url_for("apps.auth_callback",
                                                                     _external=True,
                                                                     _scheme="https")},
                                 auth=(os.getenv("NOTION_CLIENT_ID"), os.getenv("NOTION_CLIENT_SECRET"))
                                 )
        creds = response.json()
        return creds, user, app_name, None
    elif app_name == GOOGLE_MAIL_APP_NAME or app_name == GOOGLE_CAL_APP_NAME:
        scopes = args["scope"].split(" ")
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=scopes, state=state)
        flow.redirect_uri = flask.url_for('apps.auth_callback', _external=True, _scheme="https")
        authorization_response = url
        authorization_response = authorization_response.replace("http://", "https://")

        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        claims = verify_oauth2_token(credentials.id_token, Request(), audience=os.getenv('GOOGLE_CLIENT_ID'))
        return credentials, user, app_name, claims
