import logging
import os
from threading import Thread

from configs import ChannelConf
from constants import WHATSAPP_CHANNEL, TELEGRAM_CHANNEL, SLACK_CHANNEL, iMESSAGE_CHANNEL
from data_access import (
  delete_user_events, delete_user_channel, get_user_channels,
  get_channel, get_verification_request, update_verification_request,
  create_verification_request, update_channel_config
)
from util.app import generate_code
from util.auth import state_store, authorize_url_generator

logger = logging.getLogger()
text_allowed = [WHATSAPP_CHANNEL, iMESSAGE_CHANNEL]

chat_links = {
  WHATSAPP_CHANNEL: f"https://wa.me/{os.getenv('WA_NUM')}?text=",
  TELEGRAM_CHANNEL: f"https://t.me/{os.getenv('TG_NAME')}",
  iMESSAGE_CHANNEL: f"https://bcrw.apple.com/urn:biz:{os.getenv('APPLE_BUSINESS_ID')}?body="
}


class ChannelService:

  @classmethod
  def create_channel(cls, channel: str, user: str) -> [bool, str, dict]:
    verification_code = int(generate_code())
    if channel == SLACK_CHANNEL:
      state = state_store.issue()
      verification_link = authorize_url_generator.generate(state)
    else:
      verification_link = f"{chat_links[channel]}{verification_code if channel in text_allowed else ''}"
    verification_request = get_verification_request(user)
    if verification_request:
      updated = update_verification_request(verification_request.user_id, verification_code, channel=channel)
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
  def get_channel(cls, user_id: str, name: str) -> [bool, str, dict]:
    channel = get_channel(user_id, name)
    if channel is None:
      return False, 'No channel found.', None
    return True, 'Channel found.', {
      # 'sender_id': channel.sender_id,
      'channel': channel.name,
      'config': ChannelConf.from_string(channel.config)
    }

  @classmethod
  def get_channels(cls, uuid: str) -> [bool, str, list]:
    channels = get_user_channels(uuid)
    if channels is None:
      return False, 'No channels found.', None
    return True, 'Channels found.', [{
      'sender_id': channel.sender_id,
      'channel': channel.name,
      'config': ChannelConf.from_string(channel.config)
    } for channel in channels]

  @classmethod
  def remove_channel(cls, user_id: str, sender_id: str) -> [bool, str]:
    status, message = delete_user_channel(user_id, sender_id)
    Thread(target=cls.delete_events, args=[user_id]).run()
    return status, message

  @classmethod
  def delete_events(cls, user_id: str):
    delete_user_events(user_id)

  @classmethod
  def update_channel_conf(cls, user_id: str, channel_name: str, config: dict) -> [bool, str]:
    # validate channel config
    try:
      conf = ChannelConf(**config)
      if not update_channel_config(user_id, channel_name, f"{conf}"):
        return False, 'Unable to update channel config.'
      return True, 'Channel config updated.'
    except Exception as e:
      logger.error(e)
      return False, 'Unable to update channel config.'
