import json
import logging
import os
import uuid

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from werkzeug import Request, Response

import services
from exceptns import UserNotFoundException
from routes.user import VERSION

SECURITY_EXCLUSIONS = [f'/{VERSION}/user/login',
                       f'/{VERSION}/admin/find_user',
                       f'/{VERSION}/wait', '/',
                       f'/logo', f'/logowtext',
                       '/auth_callback', '/webhooks/stripe', '/v0/subscription', '/v0/billing_portal']

user_service = services.UserService()
logger = logging.getLogger(__name__)


class Middleware:
  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    request = Request(environ)

    if request.path in SECURITY_EXCLUSIONS or request.method == "OPTIONS":
      return self.app(environ, start_response)

    if request.path == '/v0/application' and request.method == 'POST':
      return self.app(environ, start_response)

    auth = request.headers.get("Authorization")
    if not auth:
      res = Response(json.dumps({'error': 'Authorization failed'}), mimetype='application/json', status=401)
      return res(environ, start_response)

    try:
      claims = verify_oauth2_token(auth.split(" ")[1], requests.Request(), audience=os.getenv('GOOGLE_CLIENT_ID'))
    except ValueError as e:
      logger.error(e)
      res = Response(json.dumps({"error": f"Invalid authorization. {e}"}), mimetype='application/json', status=401)
      return res(environ, start_response)

    if not claims['email_verified']:
      res = Response(json.dumps({"error": "User is not registered by Google."}),
                     mimetype="application/json", status=401)
      return res(environ, start_response)

    __id__: uuid.UUID = uuid.uuid5(uuid.NAMESPACE_URL, claims['email'])
    try:
      user = user_service.find_user(__id__)
      environ['user'] = user
    except UserNotFoundException:
      res = Response(json.dumps({'error': 'User is not registered by babs.ai'}),
                     mimetype='application/json', status=401)
      return res(environ, start_response)
    except Exception as e:
      logger.error(e)
      res = Response(json.dumps({'error': 'Could not authenticate user. Contact admin'}),
                     mimetype='application/json', status=500)
      return res(environ, start_response)

    return self.app(environ, start_response)
