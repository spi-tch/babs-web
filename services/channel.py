import logging
import os
from threading import Thread

from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from data_access import VerificationRequest, Channel, delete_user_events, delete_user_channel, get_user_channels, \
  get_channel, get_verification_request, update_verification_request, create_verification_request
from util.app import db, generate_code

logger = logging.getLogger()
chat_links = {
  "whatsapp": f"https://wa.me/{os.getenv('WA_NUM')}?text=",
  "telegram": f"https://t.me/{os.getenv('TG_NAME')}",
}


class ChannelService:

  @classmethod
  def create_channel(cls, channel: str, user: str) -> [bool, str, dict]:
    verification_code = int(generate_code())
    verification_link = f"{chat_links[channel]}{verification_code if channel == 'whatsapp' else ''}"
    verification_request = get_verification_request(user)
    if verification_request:
      updated = update_verification_request(verification_request, verification_code)
      if updated:
        return True, 'Verification request created.', {
          'verification_code': verification_code,
          'verification_link': verification_link
        }
    if create_verification_request(user, channel, verification_code):
      return True, 'Verification request created.', {
        'verification_code': verification_code,
        'verification_link': verification_link
      }
    return False, 'Unable to create verification request.', None

  @classmethod
  def get_channel(cls, request: dict) -> [bool, str, dict]:
    channel = get_channel(request['user_uuid'])
    if channel is None:
      return False, 'No channel found.', None
    return True, 'Channel found.', {
      'sender_id': channel.sender_id,
      'channel': channel.name,
      'verified': channel.verified
    }

  @classmethod
  def get_channels(cls, uuid: str) -> [bool, str, list]:
    channels = get_user_channels(uuid)
    if channels is None:
      return False, 'No channels found.', None
    return True, 'Channels found.', [{
      'sender_id': channel.sender_id,
      'channel': channel.name
    } for channel in channels]


  @classmethod
  def remove_channel(cls, user_id: str, sender_id: str) -> [bool, str]:
    status, message = delete_user_channel(user_id, sender_id)
    Thread(target=cls.delete_events, args=[user_id]).run()
    return status, message

  @classmethod
  def delete_events(cls, user_id: str):
    delete_user_events(user_id)
