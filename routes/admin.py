import os

from flask import Blueprint, request

import services

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"

find = Blueprint('find', __name__)
user_service = services.UserService()


@find.route(f"/{VERSION}/admin/find_user", methods=['GET'])
def admin_find_user():
  phone = request.args.get("phone")

  user_info = user_service.find_user_by_phone(phone)
  message = {"success": True, "message": "Found user", "data": user_info}
  return message, 200
