import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'abc+1s'
  SQLALCHEMY_COMMIT_ON_TEARDOWN = True
  # FLASKY_MAIL_SUBJECT_PREFIX = '[lushg]'
  # FLASKY_MAIL_SENDER = 'Admin<lushg-tcxg@qq.com>'

  staticmethod
  def init_app(app):
    pass

class DevelopmentConfig(Config):
  DEBUG = True
  MAIL_SERVER = 'smtp.qq.com'
  MAIL_PORT = 587
  MAIL_USE_TLS = True
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

class TestingConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

class ProductionConfig(config):
  SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,
  'default': DevelopmentConfig
}
