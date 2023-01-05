import logging
import uuid

import requests
from sqlalchemy import update

from data_access import GoogleCreds
from util.app import db

logger = logging.getLogger(__name__)


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


class AuthService:
  @classmethod
  def store_google_creds(cls, user_id: uuid.UUID, credentials) -> [bool, str]:
    """
    This function will update the credentials of a Google user. This also includes
    revocation and partial authorization
    :param user_id: The user's uuid
    :param credentials: Google Credentials
    :return: tuple (bool, str)
    """
    if cls.get_google_creds(str(user_id)):
      return cls.update_creds(credentials_to_dict(credentials), user_id)

    new_creds = GoogleCreds(
      user=user_id,
      token=credentials.token,
      refresh_token=credentials.refresh_token,
      token_uri=credentials.token_uri,
      client_id=credentials.client_id,
      client_secret=credentials.client_secret,
      scopes=credentials.scopes
    )

    try:
      db.session.add(new_creds)
      db.session.commit()
    except Exception as e:
      logger.error(e)
      db.session.rollback()
      return False, "Unable to store credentials."
    finally:
      db.session.close()

    return True, "User credentials successfully stored."

  @classmethod
  def get_google_creds(cls, user_id: str):
    try:
      creds = GoogleCreds.query.filter_by(user=user_id).first()
      if creds is None:
        return None
      return creds
    except Exception as e:
      logger.error(e)
      db.session.rollback()
    finally:
      db.session.close()

  @classmethod
  def update_creds(cls, new_creds, user_id):

    try:
      statement = (update(GoogleCreds)
                   .where(GoogleCreds.user == user_id)
                   .values(**new_creds)
                   .execution_options(synchronize_session=False))
      db.session.execute(statement=statement)
      db.session.commit()
    except Exception as e:
      logger.error(e)
      db.session.rollback()
      return False, "Unable to update user creds"
    finally:
      db.session.close()

  @classmethod
  def revoke_creds(cls, user_id):
    # Call Google API to revoke the token
    # Delete the creds from the database
    creds = cls.get_google_creds(user_id)
    response = requests.post('https://oauth2.googleapis.com/revoke', params={'token': creds.token},
                             headers={'content-type': 'application/x-www-form-urlencoded'})
    if response.status_code != 200:
      return False, "Unable to revoke credentials"
    try:
      creds = GoogleCreds.query.filter_by(user=user_id).first()
      if creds is None:
        return False, "No credentials found."
      db.session.delete(creds)
      db.session.commit()
    except Exception as e:
      logger.error(e)
      db.session.rollback()
      return False, "Unable to delete application."
    finally:
      db.session.close()

