import enum

from util.app import db


class ChannelEnum(enum.Enum):
  whatsapp = 'WHATSAPP'
  telegram = 'TELEGRAM'


class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String, nullable=False, index=True)
  phone_number = db.Column(db.String, nullable=False)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         server_onupdate=db.func.current_timestamp())
  email = db.Column(db.String(50), nullable=True)
  dob = db.Column(db.DATE, nullable=False)
  country = db.Column(db.String(2), nullable=False)
  verified = db.Column(db.Boolean, nullable=False)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  channel = db.Column(db.Enum(ChannelEnum), nullable=False)

  def __repr__(self):
    return f'User: {self.first_name} {self.last_name}; Country: {self.country}'


class VerificationRequest(db.Model):
  __tablename__ = 'verification_requests'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.String, nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  verification_code = db.Column(db.Integer, nullable=False)
