import enum
import logging

from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from util.app import db

logger = logging.getLogger(__name__)


class ChannelEnum(enum.Enum):
  whatsapp = 'WHATSAPP'
  telegram = 'TELEGRAM'
  imessage = 'IMESSAGE'
  messenger = 'FACEBOOK_MESSENGER'
  snapchat = 'SNAPCHAT'
  slack = 'SLACK'


class Channel(db.Model):
  __tablename__ = 'channels'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  user_uuid = db.Column(db.String, nullable=False)
  sender_id = db.Column(db.String, nullable=False, index=True)
  config = db.Column(db.String, nullable=True, default='default')


class VerificationRequest(db.Model):
  __tablename__ = 'verification_requests'
  user_id = db.Column(db.String, nullable=False, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  verification_code = db.Column(db.Integer, nullable=False)
  channel = db.Column(db.String, nullable=False)


def delete_user_channel(user_id, sender_id):
  try:
    channel = Channel.query.filter_by(sender_id=sender_id, user_uuid=user_id).first()
    if channel is None:
      return False, 'No channel found.'

    db.session.delete(channel)
    db.session.commit()
    return True, 'Channel removed.'
  except OperationalError as e:
    db.session.rollback()
    logger.error('Could not remove channel.', e)
    return False, 'Could not remove channel.'
  finally:
    db.session.close()


def get_user_channels(user_id):
  try:
    channels = Channel.query.filter_by(user_uuid=user_id).all()
    return channels
  except OperationalError as e:
    db.session.rollback()
    logger.error('Could not get verification request.', e)
    return False
  finally:
    db.session.close()


def get_channel(user_id, name):
  try:
    channel = Channel.query.filter_by(user_uuid=user_id, name=name).first()
    return channel
  except OperationalError as e:
    db.session.rollback()
    logger.error('Could not get verification request.', e)
    return False
  finally:
    db.session.close()


def get_verification_request(user_id):
  try:
    verification_request = VerificationRequest.query.filter_by(user_id=user_id).first()
    return verification_request
  except OperationalError as e:
    db.session.rollback()
    logger.error('Could not get verification request.', e)
    return False
  finally:
    db.session.close()


def update_verification_request(user_id: str, verification_code: int, channel: str):
  try:
    statement = (update(VerificationRequest)
                 .where(VerificationRequest.user_id == user_id)
                 .values({"verification_code": verification_code, "channel": channel})
                 .execution_options(synchronize_session=False))
    db.session.execute(statement=statement)
    db.session.commit()
    return True
  except OperationalError as e:
    db.session.rollback()
    logger.error('Could not update verification request.', e)
    return False
  finally:
    db.session.close()


def create_verification_request(user_id: str, channel: str, verification_code: int):
  try:
    verification_request = VerificationRequest(
      channel=channel,
      user_id=user_id,
      verification_code=verification_code
    )
    db.session.add(verification_request)
    db.session.commit()
    return True

  except OperationalError as e:
    db.session.rollback()
    logger.error('Unable to create verification request.', e)
    return False
  finally:
    db.session.close()


def update_channel_config(user_id: str, name: str, config: str):
  try:
    statement = (update(Channel)
                 .where(Channel.user_uuid == user_id)
                 .where(Channel.name == name)
                 .values({"config": config})
                 .execution_options(synchronize_session=False))
    db.session.execute(statement=statement)
    db.session.commit()
    return True
  except OperationalError as e:
    db.session.rollback()
    logger.error('Could not update channel config.', e)
    return False
  finally:
    db.session.close()
