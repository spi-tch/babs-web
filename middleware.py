from werkzeug import Request

from routes.user import VERSION

SECURITY_EXCLUSIONS = [f'/{VERSION}/user/register']


class Middleware:
  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    request = Request(environ)
    if request.path in SECURITY_EXCLUSIONS:
      return self.app(environ, start_response)
    else:
      # TODO: authorize user
      return self.app(environ, start_response)
