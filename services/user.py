import uuid
from threading import Thread

from sqlalchemy.orm import scoped_session

from data_access import User, VerificationRequest, DBQuery
from exceptions import UserNotFoundException, DuplicateUserException
from util.app import db, get_phone_number, generate_code
from util.twilio import send_verification_code


def build_user_object(user):
  return {
    'uuid': user.uuid,
    'email': user.email,
    'phone_number': user.phone_number,
    'dob': user.dob,
    'verified': user.verified,
    'channel': user.channel.name,
    'country': user.country,
    'is_admin': user.is_admin,
    'first_name': user.first_name,
    'last_name': user.last_name
  }


class UserService:
  def __init__(self):
    self.user_query: DBQuery[User] = db.session.query(User)
    self.verification_query: DBQuery[VerificationRequest] = db.session.query(VerificationRequest)
    self.session: scoped_session = db.session

  def find_user(self, user_id: uuid.UUID):
    user = self.user_query.filter(User.uuid == str(user_id)).first()
    if user is None:
      raise UserNotFoundException('Unable to find user.')
    return user

  def create_user(self, request: dict):
    __id__ = uuid.uuid5(uuid.NAMESPACE_URL, request['email'])

    try:
      if old_user := self.find_user(__id__):
        if old_user.verified:
          raise DuplicateUserException('A user with this email already exists.')
        self.send_verification(old_user)
        old_user = build_user_object(old_user)
        return True, 'User created, not verified. Verification code sent', old_user

    except UserNotFoundException:
      pass  # We create the user instead

    new_user = User(
      first_name=request['first_name'],
      last_name=request['last_name'],
      uuid=__id__,
      email=request['email'],
      phone_number=request['phone_number'],
      dob=request['dob'],
      verified=False,
      is_admin=request.get('is_admin', False),
      channel=request['channel'],
      country=request['country']
    )
    self.session.add(new_user)
    self.session.commit()

    user = self.find_user(__id__)

    if user:
      self.send_verification(user)

    return True, 'User created on DB', build_user_object(user)

  def verify_user(self, request: dict) -> (bool, str):
    if code_record := self.verification_query.filter(
        VerificationRequest.verification_code == request['verification_code'],
        VerificationRequest.user_id == request['uuid']
    ):
      status, message = self.update_user({
        'verified': True,
        'uuid': request['uuid']
      })
      if not status:
        return False, message
      self.delete_verification_code(code_record)
      return True, 'Successfully verified user.'
    return False, 'code is invalid (incorrect)'

  def save_verification_code(self, request):
    try:
      code = VerificationRequest(
        user_id=request['uuid'],
        verification_code=request['code']
      )
      self.session.add(code)
      self.session.commit()
    except Exception:
      return False, 'Unable to save verification code'

  @classmethod
  def delete_verification_code(cls, data: DBQuery):
    try:
      count = data.delete(synchronize_session='evaluate')
      print(count)
    except Exception as e:
      pass  # TODO: Log error

  def update_user(self, request: dict, user: DBQuery = None):
    if user is None:
      try:
        user = self.session.query(User).filter({
          User.uuid: request['uuid']
        }).with_hint(User, 'USE INDEX uuid')
      except KeyError:
        return False, 'uuid is missing'

    count = user.update({
      key: value for key, value in request.items()
    }, synchronize_session='evaluate')
    if count == 0:
      return False, 'Update failed'
    return True, 'Update succeeded'

  def send_verification(self, user):
    phone_number = get_phone_number(user.country, user.phone_number)
    code = generate_code()
    # Send code to user through channel
    twilio_thread = Thread(target=send_verification_code,
                           args=(phone_number, user.channel.name, code))
    twilio_thread.start()

    # Save to DB
    self.save_verification_code({'uuid': user.uuid, 'code': code})

  def find_user_by_phone(self, phone_number: str):
    user = self.user_query.filter(User.phone_number == f"+{phone_number}").first()
    return build_user_object(user)
