import logging
import os
import uuid
from threading import Thread

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from data_access import User, VerificationRequest, DBQuery, WaitList
from exceptns import UserNotFoundException
from util.app import db, get_phone_number, generate_code
from util.twilio import send_verification_code

logger = logging.getLogger()


def build_user_object(user: User):
  channel = None if not user.channel else user.channel.name
  return {
    'uuid': user.uuid,
    'email': user.email,
    'phone_number': user.phone_number or None,
    'dob': user.dob or None,
    'verified': user.verified,
    'channel': channel,
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
      if existing_user.verified:
        existing_user = build_user_object(existing_user)
        return True, 'User details', existing_user

      return True, 'User exists, but not verified', build_user_object(existing_user)

    new_user = User(
      first_name=claims['given_name'],
      last_name=claims['family_name'],
      uuid=__id__,
      email=claims['email'],
      verified=False,
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
  def verify_user(cls, user: User, code: int) -> (bool, str):
    try:
      code_record = VerificationRequest.query.filter(VerificationRequest.verification_code == code,
                                                     VerificationRequest.user_id == user.uuid)
      if code_record.first():
        status, message, _ = cls.update_user({
          'verified': True,
          'uuid': user.uuid
        })
        if not status:
          return False, message
        cls.delete_verification_code(code_record)
        db.session.commit()
        return True, 'Successfully verified user.'
      db.session.commit()
      return False, 'code is invalid (incorrect)'
    except OperationalError:
      db.session.rollback()
    finally:
      db.session.close()

  @classmethod
  def delete_verification_code(cls, data: DBQuery):
    """
    This method does not commit deletes.
    Ensure you commit the session after deletion.
    """
    try:
      count = data.delete(synchronize_session='evaluate')
      print(count)
    except Exception as e:
      logger.error(e)

  @classmethod
  def update_user(cls, request: dict, user: User = None) -> [bool, str, dict]:
    if user is None:
      try:
        user = cls.find_user(request['uuid'])
      except KeyError:
        return False, 'uuid is missing', {}

    old_phone = user.phone_number
    old_channel = user.channel

    try:
      statement = (update(User)
                   .where(User.uuid == user.uuid)
                   .values(**request)
                   .execution_options(synchronize_session=False))

      db.session.execute(statement=statement)
      db.session.commit()

      user = cls.find_user(uuid.UUID(user.uuid))
      user_info = build_user_object(user)

      if old_phone != user.phone_number or old_channel != user.channel:
        cls.send_verification(user)
        return True, 'Phone number and/or channel updated. Verification code sent', user_info
      return True, 'Update succeeded', user_info

    except Exception as e:
      logger.error(e)
      db.session.rollback()
      return False, 'Update failed', {}
    finally:
      db.session.close()

  @classmethod
  def send_verification(cls, user):
    phone_number = get_phone_number(user.phone_number)
    code = generate_code()
    # Send code to user through channel
    messenger_thread = Thread(target=send_verification_code,
                              args=(phone_number, user.channel.name, code))
    messenger_thread.start()

    # Save to DB
    cls.save_verification_code({'uuid': user.uuid, 'code': code})

  @classmethod
  def find_user_by_phone(cls, phone_number: str):
    if phone_number.startswith("+"):
      phone_number = phone_number[1:]
    user = None
    try:
      user = User.query.filter(User.phone_number == phone_number).first()
      return build_user_object(user)
    except OperationalError:
      User.query.session.rollback()
      return user

  @classmethod
  def save_verification_code(cls, request):
    try:
      if code := VerificationRequest.query.filter(VerificationRequest.user_id == request['uuid']).first():
        statement = (update(VerificationRequest)
                     .where(User.uuid == code.user_id)
                     .values({"verification_code": request['code']})
                     .execution_options(synchronize_session=False))
        db.session.execute(statement=statement)
      else:
        code = VerificationRequest(
          user_id=request['uuid'],
          verification_code=request['code']
        )
        db.session.add(code)
      db.session.commit()
    except OperationalError:
      db.session.rollback()
      return False, 'Unable to save verification code'
    finally:
      db.session.close()

  @classmethod
  def add_to_waitlist(cls, email) -> bool:
    try:
      if waiter := WaitList.query.filter(WaitList.email == email).first():
        return True
      else:
        waiter = WaitList(
          email=email,
        )
        db.session.add(waiter)
      db.session.commit()
      return True
    except OperationalError:
      db.session.rollback()
      return False
    finally:
      db.session.close()
