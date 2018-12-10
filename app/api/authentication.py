from flask import g, jsonify, request
# from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .decorators import login_required
from .errors import unauthorized, forbidden, bad_request
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
  if not user or not user.confirmed:
    return False
  g.current_user = user
  g.token_used = False
  return user.verify_password(password)

@api.before_request
def before_request():
  if (request.method == 'OPTIONS'):
    return jsonify({ 'success': True })
  authString = request.headers.get('Authorization', '')
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
    return unauthorized('非法请求, 请登录', True)
  return jsonify({'token': g.current_user.generate_auth_token(expiration=3600 * 24 * 30), 'expiration': 3600 * 24 * 30})

@api.route('/user/', methods=['GET'])
@login_required()
def get_user_by_token():
  if g.current_user.is_anonymous:
    return unauthorized('非法请求, 请登录')
  return jsonify(g.current_user.to_json())

@api.route('/register/', methods=["POST"])
def register():
  data = request.json
  user = User.query.filter_by(email = data['email']).first()
  if user:
    if user.confirmed:
      res = jsonify({ 'message': '该邮箱已被注册', 'notify': True })
    else:
      res = jsonify({ 'message': '该邮箱已被注册，并且重新发送激活邮件至你的邮箱，请注意查收', 'notify': True })
      token = user.generate_confirmation_token()
      send_email(user.email, '账号确认', 'register', url = data["url"] + '?token=%s&email=%s'%(token, data['email']), user = user)
    res.status_code = 403
    return res
  else:
    user = User.query.filter_by(username = data['username']).first()
    if user:
      res = jsonify({ 'message': '该用户名已被使用', 'notify': True })
      res.status_code = 403
      return res
  user = User(email = data['email'], username = data['username'], password = data['password'])
  db.session.add(user)
  try:
    db.session.commit()
  except:
    res = jsonify({ "error": "bad request", "message": "参数错误" })
    res.status_code = 403
    return res
  token = user.generate_confirmation_token()
  send_email(user.email, '账号确认', 'register', url = data["url"] + '?token=%s'%token, user = user)
  return jsonify({ "success": True })

@api.route('/confirm/', methods=["POST"])
def confirm():
  token = request.json.get('token', None)
  email = request.json.get('email', None)
  if token and email:
    user = User.query.filter_by(email = email).first()
    if user:
      if user.confirmed:
        return  jsonify({ 'message': '该账号已经激活，请登录。', 'notify': True })
      if  user.confirm(token):
        db.session.commit()
        return jsonify({ 'message': '激活账户成功，请登录', 'notify': True })
  return bad_request('激活链接无效！', True)

@api.route('/change-password/', methods=['POST'])
@login_required()
def change_password():
  oldPasswd = request.json.get('oldPasswd')
  newPasswd = request.json.get('newPasswd')
  if g.current_user.verify_password(oldPasswd) and newPasswd:
    g.current_user.password = newPasswd
    db.session.add(g.current_user)
    db.session.commit()
    return jsonify({ 'message': '修改密码成功', 'notify': True })
  errorMsg = '旧密码验证失败' if newPasswd else '新密码不能为空'
  return bad_request(errorMsg, True)

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
