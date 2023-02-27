import logging

from constants import GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME
from data_access import get_app_by_user, create_app, get_user_app, delete_app
from util.watch import watch_gmail, delete_gmail_watch

logger = logging.getLogger(__name__)


class AppService:
  @classmethod
  def add_app(cls, app_name: str, user: dict, creds: dict) -> [bool, str, dict]:

    app = get_app_by_user(user["uuid"], app_name)
    if app:
      return False, 'User already has this application.', None
    if create_app(app_name, user["uuid"]):
      if app_name == GOOGLE_MAIL_APP_NAME:
        watch_gmail(user, creds)
      elif app_name == GOOGLE_CAL_APP_NAME:
        # watch_calendar(user["uuid"], creds)
        pass
      return True, 'Application added.', {'app': app_name}
    return False, f'Could not create {app_name} for user.', None

  @classmethod
  def get_apps(cls, user: str) -> [bool, str, list]:
    apps = get_user_app(user)
    if apps is None:
      return False, 'No apps found.', None
    return True, 'Apps found.', [app.name for app in apps]

  @classmethod
  def remove_app(cls, user: str, app_name: str) -> [bool, str]:
    # from .auth import AuthService
    # todo: revoke credentials
    # revoked, message = AuthService().revoke_creds(user)
    # if not revoked:
    #   return False, message

    app = get_app_by_user(user, app_name)
    if app is None:
      return False, 'App not found.'
    if app_name == GOOGLE_MAIL_APP_NAME:
      delete_gmail_watch(user)
    elif app_name == GOOGLE_CAL_APP_NAME:
      # delete_calendar_watch(user)
      pass
    if delete_app(app):
      return True, 'App removed.'
    return False, 'Could not remove app.'
