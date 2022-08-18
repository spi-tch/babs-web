# This project is custom-licensed by Babs Technologies

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
  KEY = os.getenv('HTTP_SECRET_KEY')
  SQLALCHEMY_DATABASE_URI = (f"{os.getenv('DB_SCHEME')}://{os.getenv('DB_USER')}:"
                             f"{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:"
                             f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  @staticmethod
  def init_app(app):
    pass


class DevConfig(Config):
  DEBUG = True

  @classmethod
  def init_app(cls, app):
    pass


class TestConfig(Config):
  TESTING = True

  @classmethod
  def init_app(cls, app):
    pass


class ProductionConfig(Config):

  @classmethod
  def init_app(cls, app):
    Config.init_app(app)

    # TODO: Configure mail


APP_CONFIG = {
  'dev': DevConfig,
  'test': TestConfig,
  'production': ProductionConfig,
  'default': DevConfig
}

