import logging
import uuid

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from services import AuthService, UserService, build_user_object, credentials_to_dict

logger = logging.getLogger(__name__)
mail_topic = "projects/babs-ai-test/topics/gmail"
calendar_topic = "projects/babs-ai-test/topics/calendar"


def get_credentials(creds: dict):
  """Returns the credentials for the given user."""
  return Credentials(**creds)


def get_gmail_service(creds: dict):
  """Returns a gmail service object."""
  credentials = get_credentials(creds)
  return build("gmail", "v1", credentials=credentials)


def watch_gmail(user: dict, creds: dict) -> None:
  """Watches the user's gmail inbox for new messages."""
  service = get_gmail_service(creds)
  watch_request_body = {"labelIds": ["INBOX"], "topicName": mail_topic}
  service.users().watch(userId=user["email"], body=watch_request_body).execute()
  logger.info(f"Watching gmail for {user['email']}")


def get_calendar_service(creds: dict):
  """Returns a calendar service object."""
  credentials = get_credentials(creds)
  return build("calendar", "v3", credentials=credentials)


def watch_calendar(user: dict, creds: dict) -> None:
  """Watches the user's calendar for new events."""
  service = get_calendar_service(creds)
  watch_request_body = {"labelIds": ["INBOX"], "topicName": calendar_topic}
  service.users().watch(userId=user["email"], body=watch_request_body).execute()
  logger.info(f"Watching calendar for {user['email']}")


def delete_gmail_watch(user_id: str) -> None:
  """Deletes the gmail watch for the given user."""
  user = UserService.find_user(uuid.UUID(user_id))
  user = build_user_object(user)
  creds = credentials_to_dict(AuthService.get_google_creds(user_id))
  service = get_gmail_service(creds)
  service.users().stop(userId=user["email"]).execute()
  print(f"Deleted gmail watch for {user['email']}")


def delete_calendar_watch(user_id: str) -> None:
  """Deletes the calendar watch for the given user."""
  user = UserService.find_user(uuid.UUID(user_id))
  user = build_user_object(user)
  creds = credentials_to_dict(AuthService.get_google_creds(user_id))
  service = get_calendar_service(creds)
  watch = service.users().watch(userId=user["email"]).execute()
  service.users().stop(userId=user["email"], id=watch["id"]).execute()
  print(f"Deleted calendar watch for {user['email']}")
