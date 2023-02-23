import logging

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


def create_app(name, user_uuid):
  try:
    app = Application(name=name, user_uuid=user_uuid)
    db.session.add(app)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False


def get_app_by_user(user_id, app):
  try:
    app = Application.query.filter_by(user_uuid=user_id, name=app).first()
    return app
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None


def get_user_app(user_id):
  try:
    apps = Application.query.filter_by(user_uuid=user_id).all()
    return apps
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None


def delete_app(app):
  try:
    db.session.delete(app)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
