import logging
import os

from flask import Blueprint, request

import services

channel = Blueprint('channel', __name__)

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

logger = logging.getLogger(__name__)
channel_service = services.ChannelService()


@channel.route(f'/{VERSION}/channel/<channel>', methods=['POST'])
def add_channel(channel):
  channel_name = request.view_args["channel"]

  if not channel_name:
    return {'message': 'Channel name is required', 'success': False}, 400

  try:
    status, message, data = channel_service.create_channel(channel_name, request.environ['user'].uuid)
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True, 'data': data}, 200
  except Exception as e:
    logger.error(e)
    return {'message': 'Unable to create channel', 'success': False}, 500


# Get all channels for user
@channel.route(f'/{VERSION}/channel', methods=['GET'])
def get_channels():
  try:
    status, message, data = channel_service.get_channels(request.environ['user'].uuid)
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True, 'data': data}, 200
  except Exception as e:
    logger.error(e)
    return {'message': 'Unable to get channels', 'success': False}, 500


# @channel.route(f'/{VERSION}/channel', methods=['GET'])
# def get_channel():
#   try:
#     status, message, data = channel_service.get_channel(request.environ['user'].uuid)
#     if not status:
#       return {'message': message, 'success': False}, 400
#     return {'message': message, 'success': True, 'data': data}, 200
#   except Exception as e:
#     logger.error(e)
#     return {'message': 'Unable to get channel', 'success': False}, 500


@channel.route(f'/{VERSION}/channel/<channel_id>', methods=['GET'])
def get_channel_by_id(channel_id):
  try:
    status, message, data = channel_service.get_channel_by_id(channel_id)
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True, 'data': data}, 200
  except Exception as e:
    logger.error(e)
    return {'message': 'Unable to get channel', 'success': False}, 500
