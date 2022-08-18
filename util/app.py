import os
from random import randint

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import APP_CONFIG

db: SQLAlchemy = SQLAlchemy()
# TODO: Find a better way to do this, pycountry is useless and I don't trust phonenumbers.
CC_MAP = {
  'NG': 234,
  'US': 1
}


def create_app():
  conf_name = os.getenv('FLASK_CONFIG', 'test')
  app = Flask(__name__)
  app.config.from_object(APP_CONFIG[conf_name])
  APP_CONFIG[conf_name].init_app(app)

# DB Configuration
  configure_db(app)

# Register routes
  register_blueprint(app)

# Middleware configuration
  from middleware import Middleware
  app.wsgi_app = Middleware(app.wsgi_app)

# DB Initialize
  db.create_all()
  return app


def register_blueprint(app):
  import routes

# Users
  app.register_blueprint(routes.user.register)
  app.register_blueprint(routes.user.verify)

# Home
  app.register_blueprint(routes.home.home)


def configure_db(app: Flask):
  global db
  db = SQLAlchemy(app)


def get_phone_number(country, phone_number) -> str:
  return f"+{CC_MAP[country]}{phone_number}"


def generate_code() -> str:
  return str(randint(100000, 999999))
