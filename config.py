# This project is custom-licensed by Babs Technologies

import os

from util.kg import initialize_kg_countries

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_SECRET_KEY = "i23674t8eyisjd843{}P*(&"


class Config:
  KEY = os.getenv('HTTP_SECRET_KEY')
  SQLALCHEMY_DATABASE_URI = (f"{os.getenv('DB_SCHEME')}://{os.getenv('DB_USER')}:"
                             f"{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:"
                             f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
  SQLALCHEMY_POOL_SIZE = 10
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  @staticmethod
  def init_app(app):
    from babs_kg import config
    # initialize_kg_countries()
    pass


class DevConfig(Config):
  DEBUG = True

  @classmethod
  def init_app(cls, app):
    Config.init_app(app)


class TestConfig(Config):
  TESTING = True

  @classmethod
  def init_app(cls, app):
    Config.init_app(app)


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
