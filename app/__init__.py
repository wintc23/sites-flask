from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])

  mail.init_app(app)
  db.init_app(app)
  login_manager.init_app(app)

  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)
  from .api import api as api_blueprint
  app.register_blueprint(api_blueprint, url_prefix='/api')

  return app