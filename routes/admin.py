import os
import uuid

from flask import Blueprint, request

import services
from services import build_user_object

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

find = Blueprint('find', __name__)
user_service = services.UserService()


@find.route(f"/{VERSION}/admin/find_user", methods=['GET'])
def admin_find_user():
  phone = request.args.get("phone", None)
  if phone:
    user_info = user_service.find_user_by_phone(phone)
  else:
    _id = request.args.get("uuid")
    user_info = build_user_object(user_service.find_user(uuid.UUID(_id)))
  message = {"success": True, "message": "Found user", "data": user_info}
  return message, 200
