import logging
import os
from threading import Thread

from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from data_access import VerificationRequest, Channel, BabsEvent
from util.app import db, generate_code

logger = logging.getLogger()
chat_links = {
  "whatsapp": f"https://wa.me/{os.getenv('WA_NUM')}?text=",
  "telegram": f"https://t.me/{os.getenv('TG_NAME')}",
}


class ChannelService:

  @classmethod
  def create_channel(cls, channel: str, user: str) -> [bool, str, dict]:
    verification_code = generate_code()
    verification_link = f"{chat_links[channel]}{verification_code if channel == 'whatsapp' else ''}"
    try:
      request = VerificationRequest.query.filter_by(user_id=user).first()
      if request:
        statement = (update(VerificationRequest)
                     .where(VerificationRequest.user_id == user)
                     .values({"verification_code": verification_code})
                     .execution_options(synchronize_session=False))

        db.session.execute(statement=statement)
        db.session.commit()

        return True, 'Verification request created.', {
          'verification_code': verification_code,
          'verification_link': verification_link
        }

      verification_request = VerificationRequest(
        channel=channel,
        user_id=user,
        verification_code=verification_code
      )
      db.session.add(verification_request)
      db.session.commit()
      return True, 'Verification request created.', {
        'verification_code': verification_code,
        'verification_link': verification_link
      }

    except OperationalError as e:
      db.session.rollback()
      logger.error('Unable to create verification request.', e)
      return False, 'Could not create verification request.', None
    finally:
      db.session.close()

  @classmethod
  def get_channel(cls, request: dict) -> [bool, str, dict]:
    try:
      channel = Channel.query.filter_by(user_uuid=request['user_uuid']).first()
      if channel is None:
        return False, 'No channel found.', None
      return True, 'Channel found.', {
        'sender_id': channel.sender_id,
        'channel': channel.name,
        'verified': channel.verified
      }
    except OperationalError as e:
      db.session.rollback()
      logger.error('Could not get verification request.', e)
      return False
    finally:
      db.session.close()

  @classmethod
  def get_channels(cls, uuid: str) -> [bool, str, list]:
    try:
      channels = Channel.query.filter_by(user_uuid=uuid).all()
      if channels is None:
        return False, 'No channels found.', None
      return True, 'Channels found.', [{
        'sender_id': channel.sender_id,
        'channel': channel.name
      } for channel in channels]
    except OperationalError as e:
      db.session.rollback()
      logger.error('Could not get verification request.', e)
      return False
    finally:
      db.session.close()

  @classmethod
  def remove_channel(cls, user_id: str, sender_id: str) -> [bool, str]:
    try:
      channel = Channel.query.filter_by(sender_id=sender_id, user_uuid=user_id).first()
      if channel is None:
        return False, 'No channel found.'

      Thread(target=cls.delete_events, args=[user_id]).run()
      db.session.delete(channel)
      db.session.commit()
      return True, 'Channel removed.'
    except OperationalError as e:
      db.session.rollback()
      logger.error('Could not remove channel.', e)
      return False, 'Could not remove channel.'
    finally:
      db.session.close()

  @classmethod
  def delete_events(cls, user_id: str):
    try:
      delete_events_fn = BabsEvent.__table__.delete().where(BabsEvent.user_id.__eq__(user_id))
    # todo: Do not delete events, just edit sender_id to None
      db.session.execute(delete_events_fn)
      db.session.commit()
    except OperationalError as e:
      db.session.rollback()
      logger.error('Could not delete events.', e)
    finally:
      db.session.close()
