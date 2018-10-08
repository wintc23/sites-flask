from only import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@wintc.top:3306/awesome'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['DEBUG'] = 1
db = SQLAlchemy(app)
mail = Mail(app)
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
  return dict(db = db, app = app, Role = Role, User = User)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

@app.route('/api', methods=['GET'])
def ping():
  return res_json('Hello world')

class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(64), unique = True)
  users = db.relationship('User', backref='role')

  def __repr__(self):
    return "<Role %r>" % self.name

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(64), unique = True, index = True)
  role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

  def __repr__(self):
    return "<User %r>" % self.username

if __name__ == '__main__':
  manager.run()
