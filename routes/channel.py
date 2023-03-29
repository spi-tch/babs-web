import logging

from flask import Blueprint, request

import services

channel = Blueprint('channel', __name__)

logger = logging.getLogger(__name__)
channel_service = services.ChannelService()


@channel.route(f'/channel/<channel>', methods=['POST'])
def add_channel(channel):
  channel_name = request.view_args["channel"]

  if not channel_name:
    return {'message': 'Channel name is required', 'success': False}, 400

  try:
    status, message, data = channel_service.create_channel(channel_name, request.environ['user'].uuid)
    if not status:
      response = {'message': message, 'success': False}
      return response, 400
    return {'message': message, 'success': True, 'data': data}, 200
  except Exception as e:
    logger.error(e)

    response = {'message': 'Unable to create channel', 'success': False}
    return response, 500


# Get all channels for user
@channel.route(f'/channel', methods=['GET'])
def get_channel_and_channel_details():
  try:
    if name := request.args.get('channel'):
      status, message, data = channel_service.get_channel(request.environ['user'].uuid, name)
    else:
      status, message, data = channel_service.get_channels(request.environ['user'].uuid)
    if not status:
      response = {'message': message, 'success': False}
      return response, 400
    response = {'message': message, 'success': True, 'data': data}
    return response, 200
  except Exception as e:
    logger.error(e)
    response = {'message': 'Unable to get channel(s)', 'success': False}
    return response, 500


@channel.route(f'/channel', methods=['POST'])
def update_channel():
  try:
    channel_name = request.json.get('channel')
    conf = request.json.get('config')
    status, message = channel_service.update_channel_conf(request.environ['user'].uuid, channel_name, conf)
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True}, 200
  except Exception as e:
    logger.error(e)
    return {'message': 'Unable to update channel', 'success': False}, 500


@channel.route(f'/channel', methods=['DELETE'])
def delete_channel():
  try:
    sender_id = request.args.get('sender_id')
    status, message = channel_service.remove_channel(request.environ['user'].uuid, sender_id)
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True}, 200
  except Exception as e:
    logger.error(e)
    return {'message': 'Unable to delete channel', 'success': False}, 500
