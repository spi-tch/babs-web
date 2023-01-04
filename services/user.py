import logging
import os
import uuid

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from data_access import User, VerificationRequest, DBQuery, WaitList
from exceptns import UserNotFoundException
from util.app import db

logger = logging.getLogger()


def build_user_object(user: User):
  return {
    'uuid': user.uuid,
    'email': user.email,
    'dob': user.dob or None,
    'country': user.country or None,
    'is_admin': user.is_admin,
    'first_name': user.first_name,
    'last_name': user.last_name or None
  }


class UserService:

  @classmethod
  def find_user(cls, user_id: uuid.UUID):
    try:
      user = User.query.filter_by(uuid=str(user_id)).first()
      if user is None:
        raise UserNotFoundException('Unable to find user.')
      return user
    except Exception as e:
      logger.error(e)
      db.session.rollback()
      raise UserNotFoundException('Unable to find user.')
    finally:
      db.session.close()

  def login_or_register(self, request: dict) -> [bool, str, User]:

    claims = verify_oauth2_token(request['token'], requests.Request(), audience=os.getenv('GOOGLE_CLIENT_ID'))
    if not claims['email_verified']:
      raise Exception('User email has not been verified by Google.')

    __id__ = uuid.uuid5(uuid.NAMESPACE_URL, claims['email'])

    try:
      existing_user = self.find_user(__id__)
    except UserNotFoundException:
      existing_user = None
    if existing_user:
      return True, 'User already exists', build_user_object(existing_user)

    new_user = User(
      first_name=claims['given_name'],
      last_name=claims['family_name'],
      uuid=__id__,
      email=claims['email']
    )
    try:
      db.session.add(new_user)
      db.session.commit()
    except Exception as e:
      logger.error(e)
      db.session.rollback()
    finally:
      db.session.close()

    user = self.find_user(__id__)
    return True, 'User created on DB', build_user_object(user)

  @classmethod
  def delete_verification_code(cls, data: DBQuery):
    """
    This method does not commit deletes.
    Ensure you commit the session after deletion.
    """
    try:
      _ = data.delete(synchronize_session='evaluate')
    except Exception as e:
      logger.error(e)

  @classmethod
  def update_user(cls, request: dict, user: User = None) -> [bool, str, dict]:
    if user is None:
      try:
        user = cls.find_user(request['uuid'])
      except KeyError:
        return False, 'uuid is missing', {}

    try:
      statement = (update(User)
                   .where(User.uuid == user.uuid)
                   .values(**request)
                   .execution_options(synchronize_session=False))

      db.session.execute(statement=statement)
      db.session.commit()

      user = cls.find_user(uuid.UUID(user.uuid))
      user_info = build_user_object(user)

      return True, 'Update succeeded', user_info

    except Exception as e:
      logger.error(e)
      db.session.rollback()
      return False, 'Update failed', {}
    finally:
      db.session.close()

  @classmethod
  def add_to_waitlist(cls, email) -> bool:
    try:
      if _ := WaitList.query.filter(WaitList.email == email).first():
        return True
      else:
        waiter = WaitList(
          email=email,
        )
        db.session.add(waiter)
        # Thread(target=send_email, args=[email]).start()
      db.session.commit()
      return True
    except OperationalError:
      db.session.rollback()
      return False
    finally:
      db.session.close()
