import logging

from sqlalchemy import update

from util.app import db

logger = logging.getLogger(__name__)


class Application(db.Model):
  __tablename__ = 'applications'
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  user_uuid = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=True)


def create_app(name, user_uuid, email):
  try:
    app = Application(name=name, user_uuid=user_uuid, email=email)
    db.session.add(app)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False


def get_app_by_user(user_id, app, email):
  try:
    app = Application.query.filter_by(user_uuid=user_id, name=app, email=email).first()
    return app
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None


def get_app_by_email(app_name, email):
  try:
    app = Application.query.filter_by(name=app_name, email=email).first()
    return app
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None
  finally:
    db.session.close()


def get_user_app(user_id):
  try:
    apps = Application.query.filter_by(user_uuid=user_id).all()
    return apps
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None


def update_app(user_id, email):
  try:
    statement = (update(Application)
                 .where(Application.user_uuid == user_id)
                 .values(email=email)
                 .execution_options(synchronize_session=False)
                 )
    db.session.execute(statement)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()


def delete_app(app):
  try:
    db.session.delete(app)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
