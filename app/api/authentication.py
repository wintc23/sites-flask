from flask import g, jsonify, request
# from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .decorators import login_required
from .errors import unauthorized, forbidden
from .. import db
from ..email import send_email

# auth = HTTPBasicAuth()

# @auth.verify_password
def verify_password(email_or_token, password):
  if email_or_token == '':
    g.current_user = AnonymousUser()
    return True
  if password == '':
    g.current_user = User.verify_auth_token(email_or_token)
    if g.current_user:
      g.token_used = True
    else:
      g.current_user = AnonymousUser()
    return True
  user = User.query.filter_by(email = email_or_token).first()
  if not user:
    return False
  g.current_user = user
  g.token_used = False
  return user.verify_password(password)

@api.before_request
def before_request():
  if (request.method == 'OPTIONS'):
    return jsonify({ 'success': True })
  authString = request.headers.get('Authorization', '')
  print('before_request', authString)
  email_or_token = ''
  password = ''
  if ':' in authString:
    email_or_token, password = authString.split(':')
  else:
    email_or_token = authString
  res = verify_password(email_or_token, password)
  if not res:
    return unauthorized('Invalid!')

@api.route('/tokens/', methods=['POST'])
def get_token():
  if g.current_user.is_anonymous or g.token_used:
    return unauthorized('非法请求, 请登录')
  return jsonify({'token': g.current_user.generate_auth_token(expiration=3600*24*30), 'expiration': 3600})

@api.route('/user/', methods=['GET'])
@login_required()
def get_user_by_token():
  if g.current_user.is_anonymous:
    return unauthorized('非法请求, 请登录', False)
  return jsonify(g.current_user.to_json())

@api.route('/register/', methods=["POST"])
def register():
  data = request.json
  user = User(email = data['email'], username = data['username'], password = data['password'])
  db.session.add(user)
  try:
    db.session.commit()
  except:
    res = jsonify({ "error": "bad request", "message": "参数错误" })
    res.status_code = 403
    return res
  token = user.generate_confirmation_token()
  send_email(user.email, )
  return jsonify({ "success": True })

@api.after_request
def after_request(response):
  try:
    db.session.commit()
  except:
    response = jsonify({ 'error': 'database error', 'message': '数据出错，请重试' })
    response.status_code = 403
  return response

@api.teardown_request
def dbsession_clean(exception=None):
  try:
    db.session.remove()
  finally:
    pass