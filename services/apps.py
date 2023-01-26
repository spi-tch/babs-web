import logging
from threading import Thread

from sqlalchemy.exc import OperationalError

from data_access import Application
from util.app import db
from util.watch import watch_calendar, watch_gmail

logger = logging.getLogger(__name__)


class AppService:
  @classmethod
  def add_app(cls, app_name: str, user: dict, creds: dict) -> [bool, str, dict]:
    try:
      app = Application.query.filter_by(user_uuid=user["uuid"], name=app_name).first()
      # if app:
      #   return False, 'User already has this application.', None
        
      app = Application(
        user_uuid=user["uuid"],
        name=app_name
      )
      db.session.add(app)
      db.session.commit()
      if app_name == "Google Mail":
        watch_gmail(user, creds=creds)
        # Thread(target=watch_gmail, args=(user, creds)).start()
      elif app_name == "Google Calendar":
        watch_calendar(user, creds=creds)
        # Thread(target=watch_calendar, args=(user, creds)).start()
      return True, 'Application created.', {
        'app': app_name
      }
    except OperationalError as e:
      db.session.rollback()
      logger.error(f'Unable to integrate {app_name} for user.', e)
      return False, f'Could not create {app_name} for user.', None
    finally:
      db.session.close()
      
  @classmethod
  def get_apps(cls, user: str) -> [bool, str, list]:
    try:
      apps = Application.query.filter_by(user_uuid=user).all()
      if apps is None:
        return False, 'No apps found.', None
      return True, 'Apps found.', [app.name for app in apps]
    except OperationalError as e:
      db.session.rollback()
      logger.error('Could not find apps.', e)
      return False, 'Unable to find apps.', None
    finally:
      db.session.close()

  @classmethod
  def remove_app(cls, user: str, app: str) -> [bool, str]:
    from .auth import AuthService
    try:
      revoked, message = AuthService().revoke_creds(user)
      if not revoked:
        return False, message
      app = Application.query.filter_by(user_uuid=user, name=app).first()
      if app is None:
        return False, 'No application found.'
      db.session.delete(app)
      db.session.commit()
      return True, 'Application successfully removed.'
    except OperationalError as e:
      db.session.rollback()
      logger.error('Could not remove application.', e)
      return False, 'Could not remove application.'
    finally:
      db.session.close()
