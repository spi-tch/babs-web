import logging

from sqlalchemy import update

from util.app import db

logger = logging.getLogger(__name__)


class GoogleCreds(db.Model):
  __tablename__ = "google_creds"
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String, nullable=False)
  refresh_token = db.Column(db.String, nullable=False)
  token_uri = db.Column(db.String, nullable=False)
  client_id = db.Column(db.String, nullable=False)
  client_secret = db.Column(db.String, nullable=False)
  scopes = db.Column(db.ARRAY(item_type=db.String), nullable=False)
  user = db.Column(db.String, nullable=False, index=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())


def create_google_cred(user_id, credentials):
  new_creds = GoogleCreds(
    user=user_id,
    token=credentials.token,
    refresh_token=credentials.refresh_token,
    token_uri=credentials.token_uri,
    client_id=credentials.client_id,
    client_secret="credentials.client_secret",  # todo: fix this
    scopes=credentials.scopes
  )

  try:
    db.session.add(new_creds)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()


def get_google_cred(user_id):
  try:
    creds = GoogleCreds.query.filter_by(user=user_id).first()
    if creds is None:
      return None
    return creds
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None
  finally:
    db.session.close()


def update_google_cred(new_creds, user_id):
  try:
    statement = (update(GoogleCreds)
                 .where(GoogleCreds.user == user_id)
                 .values(**new_creds)
                 .execution_options(synchronize_session=False))
    db.session.execute(statement=statement)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()


def delete_google_cred(credentials):
  try:
    db.session.delete(credentials)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()

