import logging
import os
import uuid

from flask import Blueprint, request

import services
from services import build_user_object

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

find = Blueprint('find', __name__)
user_service = services.UserService()
logger = logging.getLogger(__name__)


@find.route(f"/{VERSION}/admin/find_user", methods=['GET'])
def admin_find_user():
  try:
    phone = request.args.get("phone", None)
    verified = request.args.get("verified", True)
    if phone:
      user_info = user_service.find_user_by_phone(phone)
    else:
      _id = request.args.get("uuid")
      user_info = build_user_object(user_service.find_user(uuid.UUID(_id)))

    if user_info is None:
      message = {"success": True, "message": "User not found"}
      return message, 404

    if not user_info["verified"] and verified:
      message = {"success": True, "message": "User not found"}
      return message, 404

    message = {"success": True, "message": "Found user", "data": user_info}
    return message, 200
  except Exception as e:
    logger.debug(f"Unable to fetch user.", e)
    return {"success": False, "message": "Contact admin"}, 500
