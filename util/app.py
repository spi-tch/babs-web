import os
from random import randint

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import APP_CONFIG, APP_SECRET_KEY

db: SQLAlchemy = None


def create_app():
  conf_name = os.getenv('FLASK_CONFIG', 'staging')
  template_dir = os.path.join(os.path.dirname(
    os.path.abspath(
      os.path.dirname(__file__))), 'templates')
  print(f'template folder is in: {os.path.abspath(template_dir)}')
  app = Flask(__name__, template_folder=template_dir)
  app.config.from_object(APP_CONFIG[conf_name])
  APP_CONFIG[conf_name].init_app(app)

# DB Configuration
  configure_db(app)

# Register routes
  register_blueprint(app)

# Middleware configuration
  from middleware import Middleware
  app.wsgi_app = Middleware(app.wsgi_app)

  db.create_all()
  migrate = Migrate(app, db)
# Enable CORS for all routes
  CORS(app, origins="*", send_wildcard=True, max_age=86400)

  return app


def register_blueprint(app):
  import routes

# Users
  app.register_blueprint(routes.user.user)
  # app.register_blueprint(routes.auth.auth)
  app.register_blueprint(routes.channel.channel)
  app.register_blueprint(routes.apps.apps)
  app.register_blueprint(routes.payment.subscription)

  app.config['CORS_HEADERS'] = 'Content-Type'
# Home
  app.register_blueprint(routes.home.home)
  app.secret_key = APP_SECRET_KEY

# Files
  app.register_blueprint(routes.file.file)

# Quotes
  app.register_blueprint(routes.quote.quote)


def configure_db(app: Flask):
  global db
  db = SQLAlchemy(app)
  db.init_app(app)


def get_phone_number(phone_number: str) -> str:
  return phone_number if phone_number.startswith('+') else f'+{phone_number}'


def generate_code() -> str:
  return str(randint(100000, 999999))
