from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_credentials(creds: dict):
  """Returns the credentials for the given user."""
  creds.pop("expiry")
  return Credentials(**creds)


def get_gmail_service(creds: dict):
  """Returns a gmail service object."""
  credentials = get_credentials(creds)
  return build("gmail", "v1", credentials=credentials)


def watch_gmail(user: dict, creds: dict) -> None:
  """Watches the user's gmail inbox for new messages."""
  service = get_gmail_service(creds)
  watch_request_body = {"labelIds": ["INBOX"], "topicName": f"projects/babs-ai-test/topics/gmail"}
  service.users().watch(userId=user["email"], body=watch_request_body).execute()
  print(f"Watching gmail for {user['email']}")


def get_calendar_service(creds: dict):
  """Returns a calendar service object."""
  credentials = get_credentials(creds)
  return build("calendar", "v3", credentials=credentials)


def watch_calendar(user: dict, creds: dict) -> None:
  """Watches the user's calendar for new events."""
  service = get_calendar_service(creds)
  watch_request_body = {"labelIds": ["INBOX"], "topicName": f"projects/babs-ai-test/topics/calendar"}
  service.users().watch(userId=user["email"], body=watch_request_body).execute()
  print(f"Watching calendar for {user['email']}")


def delete_gmail_watch(user: dict) -> None:
  """Deletes the gmail watch for the given user."""
  service = get_gmail_service(user["uuid"])
  watch = service.users().watch(userId=user["email"]).execute()
  service.users().stop(userId="me", id=watch["id"]).execute()
  print(f"Deleted gmail watch for {user['email']}")


def delete_calendar_watch(user: dict) -> None:
  """Deletes the calendar watch for the given user."""
  service = get_calendar_service(user["uuid"])
  watch = service.users().watch(userId=user["email"]).execute()
  service.users().stop(userId=user["email"], id=watch["id"]).execute()
  print(f"Deleted calendar watch for {user['email']}")
