import logging

from configs.apps import AppConfig
from constants import GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME
from data_access import get_app_by_user, create_app, get_user_app, delete_app, get_app_by_email, User, update_app_config
from util.watch import watch_gmail, delete_gmail_watch

logger = logging.getLogger(__name__)
GOOGLE_APPS = [GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME]


class AppService:
  @classmethod
  def add_app(cls, app_name: str, user: dict, creds: dict, email) -> [bool, str, dict]:

    if app_name in GOOGLE_APPS and get_app_by_email(app_name, email) is not None:
      return False, 'Email is already in use.', None

    app = get_app_by_user(user["uuid"], app_name, email)
    if app:
      return False, 'User already has this application.', None
    if create_app(app_name, user["uuid"], email):
      if app_name == GOOGLE_MAIL_APP_NAME:
        watch_gmail(user, creds, email)
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
    return True, 'Apps found.', [{"app": app.name, "email": app.email,
                                  "config": AppConfig.from_string(app.name, app.config)} for app in apps]

  @classmethod
  def remove_app(cls, user: User, app_name: str, email: str = None) -> [bool, str]:
    # from .auth import AuthService
    # todo: revoke credentials
    # revoked, message = AuthService().revoke_creds(user)
    # if not revoked:
    #   return False, message

    if app_name == GOOGLE_MAIL_APP_NAME and not email:
      return False, 'Email is required for this app.'
    email = email if email else user.email
    app = get_app_by_user(user.uuid, app_name, email)
    if app is None:
      return False, 'App not found.'
    if app_name == GOOGLE_MAIL_APP_NAME:
      delete_gmail_watch(user.uuid, email)
    elif app_name == GOOGLE_CAL_APP_NAME:
      # delete_calendar_watch(user)
      pass
    if delete_app(app):
      return True, 'App removed.'
    return False, 'Could not remove app.'

  @classmethod
  def update_app_conf(cls, user_id: str, app_name: str, config: dict):
    try:
      conf = AppConfig(app_name, **config)
      if not update_app_config(user_id, app_name, f"{conf}"):
        return False, 'Could not update app config.'
      return True, 'App config updated.'
    except Exception as e:
      logger.error(e)
      return False, 'Unable to update app config.'
