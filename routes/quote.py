import logging
import os

import requests
from flask import Blueprint, request, jsonify

import services

quote = Blueprint('quote', __name__)

logger = logging.getLogger(__name__)
quote_service = services.QuoteService()


@quote.route(f'/quotes', methods=['POST'])
def configure():
  request_data = request.json
  user = request.environ.get("user")
  success, message = quote_service.add_or_update_quote(user, request_data)

  if success:
    return jsonify({"success": True, "message": message}), 200
  return jsonify({"success": False, "message": "Unable to update quotes"}), 500


@quote.route(f'/quotes', methods=['GET'])
def get_quotes():
  user = request.environ.get("user")
  success, message, quote_config = quote_service.get_quote(user)
  if success:
    return jsonify({"success": True, "quotes": quote_config}), 200
  return jsonify({"success": False, "message": message}), 500

