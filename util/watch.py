import logging
import os
import uuid

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from constants import GOOGLE_CAL_APP_NAME, GOOGLE_MAIL_APP_NAME
from data_access import delete_watch, get_google_cred, create_or_update_watch
from services import UserService, build_user_object, google_cred_to_dict

logger = logging.getLogger(__name__)


def get_credentials(creds: dict):
  """Returns the credentials for the given user."""
  return Credentials(**creds)


def get_gmail_service(creds: dict):
  """Returns a gmail service object."""
  credentials = get_credentials(creds)
  return build("gmail", "v1", credentials=credentials)


def watch_gmail(user: dict, creds: dict, email) -> None:
  """Watches the user's gmail inbox for new messages."""
  try:
    service = get_gmail_service(creds)
    watch_request_body = {"labelIds": ["INBOX"], "topicName": os.getenv("GMAIL_TOPIC")}
    watch = service.users().watch(userId=email, body=watch_request_body).execute()
    create_or_update_watch(user_id=user["uuid"], app_name=GOOGLE_MAIL_APP_NAME, latest=watch["historyId"], email=email)
    logger.info(f"Watching gmail for {user['email']}")
  except Exception as e:
    logger.error(f"Unable to watch gmail for {user['email']}", e)


def get_calendar_service(creds: dict):
  """Returns a calendar service object."""
  credentials = get_credentials(creds)
  return build("calendar", "v3", credentials=credentials)


def watch_calendar(user: dict, creds: dict, email) -> None:
  """Watches the user's calendar for new events."""
  try:
    service = get_calendar_service(creds)
    watch_request_body = {"labelIds": ["INBOX"], "topicName": os.getenv("CALENDAR_TOPIC")}
    service.users().watch(userId=email, body=watch_request_body).execute()
    create_or_update_watch(user_id=user["id"], app_name=GOOGLE_CAL_APP_NAME, latest=0, email=email)
    logger.info(f"Watching calendar for {user['email']}")
  except Exception as e:
    logger.error(f"Unable to watch calendar for {user['email']}", e)


def delete_gmail_watch(user_id: str, email) -> None:
  """Deletes the gmail watch for the given user."""
  creds = google_cred_to_dict(get_google_cred(user_id, email))
  service = get_gmail_service(creds)
  try:
    service.users().stop(userId=email).execute()
  except Exception as e:
    logger.error(f"Unable to delete gmail watch for {email}", e)
    raise e
  delete_watch(user_id=user_id, app_name=GOOGLE_MAIL_APP_NAME)
  logger.info(f"Deleted gmail watch for {email}")


def delete_calendar_watch(user_id: str) -> None:
  """Deletes the calendar watch for the given user."""
  user = UserService.find_user(uuid.UUID(user_id))
  user = build_user_object(user)
  creds = google_cred_to_dict(get_google_cred(user_id, user["email"]))
  service = get_calendar_service(creds)
  watch = service.users().watch(userId=user["email"]).execute()
  service.users().stop(userId=user["email"], id=watch["id"]).execute()
  delete_watch(user_id=user_id, app_name=GOOGLE_CAL_APP_NAME)
  logger.info(f"Deleted calendar watch for {user['email']}")
