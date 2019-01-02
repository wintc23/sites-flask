import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'abc+1s'
  SQLALCHEMY_TRACK_MODIFICATIONS = True
  MAIL_SERVER = 'smtp.qq.com'
  MAIL_PORT = 465
  MAIL_USE_SSL = True
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  MAIL_SENDER = os.environ.get('MAIL_SENDER')
  MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX')
  FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
  FLASK_POSTS_PER_PAGE = 20
  FLASK_GITHUB_SECRET = os.environ.get('FLASK_GITHUB_SECRET')
  FLASK_GITHUB_CLIENT_ID = os.environ.get('FLASK_GITHUB_CLIENT_ID')

  staticmethod
  def init_app(app):
    pass

class DevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

class TestingConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

class ProductionConfig(Config):
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,
  'default': DevelopmentConfig
}
