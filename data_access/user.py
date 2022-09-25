import enum

from util.app import db


class ChannelEnum(enum.Enum):
  whatsapp = 'WHATSAPP'
  telegram = 'TELEGRAM'


class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String, nullable=False, unique=True, index=True)
  phone_number = db.Column(db.String, nullable=True, index=True)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  email = db.Column(db.String(50), nullable=True, index=True)
  dob = db.Column(db.DATE, nullable=True)
  country = db.Column(db.String(2), nullable=True)
  verified = db.Column(db.Boolean, nullable=False, default=False)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  channel = db.Column(db.Enum(ChannelEnum), nullable=True)

  def __repr__(self):
    return f'User: {self.first_name} {self.last_name}; Country: {self.country}'


class VerificationRequest(db.Model):
  __tablename__ = 'verification_requests'
  user_id = db.Column(db.String, nullable=False, primary_key=True, index=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  verification_code = db.Column(db.Integer, nullable=False)


class WaitList(db.Model):
  __tablename__ = 'wait_list'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  email = db.Column(db.String, nullable=False, index=True)
