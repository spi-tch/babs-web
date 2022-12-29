import logging

from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from data_access import Application
from util.app import db, generate_code

logger = logging.getLogger(__name__)


class AppService:
	
	@classmethod
	def add_app(cls, app_name: str, user: str) -> [bool, str, dict]:
    
    try:
      app = Application.query.filter_by(user_uuid=user, name=app_name).first()
      if app:
        return False, 'User already has this application.', None
        
      app = Application(
        user_uuid=user,
        name=app_name
      )
      db.session.add(app)
      db.session.commit()
      return True, 'Appllication created.', {
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
	def remove_app(cls, app: str, user: str) -> [bool, str]:
		try:
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