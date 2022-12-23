import enum

from util.app import db


class ChannelEnum(enum.Enum):
  whatsapp = 'WHATSAPP'
  telegram = 'TELEGRAM'
  imessage = 'IMESSAGE'
  messenger = 'FACEBOOK_MESSENGER'
  snapchat = 'SNAPCHAT'
  slack = 'SLACK'


class Channel(db.Model):
  __tablename__ = 'channel'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Enum(ChannelEnum), nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  user_uuid = db.Column(db.String, nullable=False)
  sender_id = db.Column(db.String, nullable=False, index=True)


class VerificationRequest(db.Model):
  __tablename__ = 'verification_requests'
  user_id = db.Column(db.String, nullable=False, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  verification_code = db.Column(db.Integer, nullable=False)
  channel = db.Column(db.String, nullable=False)
