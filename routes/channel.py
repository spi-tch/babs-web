import logging
import os

from flask import Blueprint, request, jsonify

import services

channel = Blueprint('channel', __name__)

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

logger = logging.getLogger(__name__)
channel_service = services.ChannelService()


@channel.route(f'/{VERSION}/channel/<channel>', methods=['POST'])
def add_channel(channel):
  channel_name = request.view_args["channel"]

  if not channel_name:
    return jsonify({'message': 'Channel name is required', 'success': False}), 400

  try:
    status, message, data = channel_service.create_channel(channel_name, request.environ['user'].uuid)
    if not status:
      response = jsonify({'message': message, 'success': False})
      response.headers.add('Access-Control-Allow-Origin', '*')
      response.headers.add('Access-Control-Allow-Credentials', 'true')
      response.status_code = 400
      return response
    response = jsonify({'message': message, 'success': True, 'data': data})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 200
    return {'message': message, 'success': True, 'data': data}, 200
  except Exception as e:
    logger.error(e)

    response = jsonify({'message': 'Unable to create channel', 'success': False})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 500
    return response


# Get all channels for user
@channel.route(f'/{VERSION}/channel', methods=['GET'])
def get_channels():
  try:
    status, message, data = channel_service.get_channels(request.environ['user'].uuid)
    if not status:
      response = jsonify({'message': message, 'success': False})
      response.headers.add('Access-Control-Allow-Origin', '*')
      response.headers.add('Access-Control-Allow-Credentials', 'true')
      return response, 400
    response = jsonify({'message': message, 'success': True, 'data': data})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 200
    return response
  except Exception as e:
    logger.error(e)
    response = jsonify({'message': 'Unable to get channels', 'success': False})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.status_code = 500
    return response


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


@channel.route(f'/{VERSION}/channel', methods=['DELETE'])
def delete_channel():
  try:
    status, message = channel_service.remove_channel(request.environ['user'].uuid, request.json['sender_id'])
    if not status:
      return {'message': message, 'success': False}, 400
    return {'message': message, 'success': True}, 200
  except Exception as e:
    logger.error(e)
    return {'message': 'Unable to delete channel', 'success': False}, 500
