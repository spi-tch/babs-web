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
  email = db.Column(db.String, nullable=False)


class NotionCreds(db.Model):
  __tablename__ = "notion_creds"
  id = db.Column(db.Integer, primary_key=True)
  access_token = db.Column(db.String, nullable=False)
  user = db.Column(db.String, nullable=False, index=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  bot_id = db.Column(db.String, nullable=False)
  workspace_id = db.Column(db.String, nullable=False)
  workspace_name = db.Column(db.String, nullable=False)
  owner = db.Column(db.String, nullable=False)


def create_google_cred(user_id, credentials, email):
  new_creds = GoogleCreds(
    user=user_id,
    token=credentials.token,
    refresh_token=credentials.refresh_token,
    token_uri=credentials.token_uri,
    client_id=credentials.client_id,
    client_secret=credentials.client_secret,
    scopes=credentials.scopes,
    email=email
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


def create_notion_cred(user_id, credentials):
  new_creds = NotionCreds(
    user=user_id,
    access_token=credentials["access_token"],
    bot_id=credentials["bot_id"],
    workspace_id=credentials["workspace_id"],
    workspace_name=credentials["workspace_name"],
    owner=str(credentials["owner"])
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


def get_google_cred(user_id, email):
  try:
    creds = GoogleCreds.query.filter_by(user=user_id, email=email).first()
    if creds is None:
      return None
    return creds
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None
  finally:
    db.session.close()


def get_notion_cred(user_id):
  try:
    creds = NotionCreds.query.filter_by(user=user_id).first()
    if creds is None:
      return None
    return creds
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return None
  finally:
    db.session.close()


def update_google_cred(new_creds: dict, user_id, email):
  try:
    statement = (update(GoogleCreds)
                 .where(GoogleCreds.user == user_id, GoogleCreds.email == email)
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


def update_notion_cred(new_creds: dict, user_id):
  try:
    statement = (update(NotionCreds)
                 .where(NotionCreds.user == user_id)
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


def add_email_to_cred(user_id, email):
  try:
    statement = (update(GoogleCreds)
                 .where(GoogleCreds.user == user_id)
                 .values(email=email)
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

