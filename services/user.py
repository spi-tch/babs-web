import logging
import os
import uuid
from threading import Thread

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

from constants import FREE_PLAN
from data_access import User, find_user_by_uuid, create_user, update_user, create_waitlister
from exceptns import UserNotFoundException
from util.mailgun import send_email

logger = logging.getLogger()


def build_user_object(user: User):
  return {
    'uuid': user.uuid,
    'email': user.email,
    'dob': user.dob or None,
    'country': user.country or None,
    'is_admin': user.is_admin,
    'first_name': user.first_name,
    'last_name': user.last_name or None,
    'timezone': user.timezone or None,
    'sub_expires_at': user.sub_expires_at or None,
    'tier': user.tier or None
  }


class UserService:

  @classmethod
  def find_user(cls, user_id: uuid.UUID):
    return find_user_by_uuid(str(user_id))

  @classmethod
  def login_or_register(cls, request: dict) -> [bool, str, User]:

    claims = verify_oauth2_token(request['token'], requests.Request(), audience=os.getenv('GOOGLE_CLIENT_ID'))
    if not claims['email_verified']:
      raise Exception('User email has not been verified by Google.')

    __id__ = uuid.uuid5(uuid.NAMESPACE_URL, claims['email'])

    try:
      existing_user = find_user_by_uuid(str(__id__))
    except UserNotFoundException:
      existing_user = None
    if existing_user:
      user = build_user_object(existing_user)
      user["new_user"] = False
      return True, 'User already exists', user

    new_user = User(
      first_name=claims['given_name'],
      last_name=claims.get('family_name', None),
      uuid=__id__,
      email=claims['email'],
      tier=FREE_PLAN,
      sub_expires_at=None
    )
    create_user(new_user)
    Thread(target=send_email, args=[claims["email"]]).start()

    user = find_user_by_uuid(str(__id__))
    user = build_user_object(user)
    user["new_user"] = True
    return True, 'User created on DB', user

  @classmethod
  def update_user(cls, request: dict, user: User = None) -> [bool, str, dict]:
    if user is None:
      try:
        user = find_user_by_uuid(request['uuid'])
      except KeyError:
        return False, 'uuid is missing', {}

    if not update_user(user, request):
      return False, 'Could not update user', {}
    find_user_by_uuid(str(user.uuid))
    user_info = build_user_object(user)
    return True, 'User update succeeded', user_info

  @classmethod
  def add_to_waitlist(cls, email) -> bool:
    create_waitlister(email)
