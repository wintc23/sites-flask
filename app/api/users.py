import os
import sys
import uuid
import json
import urllib.parse 
import urllib.request
from PIL import Image
from flask import g, jsonify, request, current_app
from ..models import User, AnonymousUser
from .errors import bad_request, not_found
from . import api
from .decorators import login_required
from .. import db
from ..models import User
@api.route('/userinfo/', methods=['GET'])
def get_user_info():
  user_id = request.args.get('id')
  user = User.query.get_or_404(user_id)
  if user:
    return jsonify(user.to_json())
  return bad_request('参数错误')

@api.route('/userid/', methods=["GET"])
def get_manager_id():
  user = User.query.filter_by(email=current_app.config['FLASK_ADMIN']).first()
  if user:
    return jsonify({ 'id': user.id })
  return not_found('无管理员信息', True)

@api.route('/save-user-avatar/', methods=['PUT'])
@login_required()
def save_avatar():
  image = request.files['image']
  filename = str(uuid.uuid1()) + image.filename
  image = Image.open(image)
  image.thumbnail((400, 400))
  dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
  upload_path = dirname + '/../files/avatar/'
  image.save(upload_path + filename)
  g.current_user.avatar = filename
  db.session.add(g.current_user)
  db.session.commit()
  return jsonify({ 'message': '上传成功', 'filename': filename, 'notify': True })

@api.route('/github_login/', methods=['GET'])
def github_login():
  code = request.args.get('code')
  secret = current_app.config['FLASK_GITHUB_SECRET']
  client_id = current_app.config['FLASK_GITHUB_CLIENT_ID']
  url = 'https://github.com/login/oauth/access_token'
  data = {
    'code': code,
    'client_id': client_id,
    'client_secret': secret
  }
  params = urllib.parse.urlencode(data).encode('utf-8')
  headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
    'Accept': 'application/json'
  }
  req = urllib.request.Request(url, params, headers)
  html = urllib.request.urlopen(req).read().decode('utf-8')
  access_data = json.loads(html)
  if access_data.get('error', ''):
    return bad_request('链接已失效，请重新登录', True)
  access_token = access_data['access_token']
  req2 = urllib.request.Request(url='https://api.github.com/user?access_token='+access_token, headers=headers)
  html2 = urllib.request.urlopen(req2).read().decode('utf-8')
  info = json.loads(html2)
  id_string = 'github' + str(info['id'])
  user = User.query.filter_by(id_string=id_string).first()
  if not user:
    avatar_url = info['avatar_url']
    if avatar_url:
      filename = str(uuid.uuid1())
      dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
      upload_path = dirname + '/../files/avatar' + filename
      urllib.request.urlretrieve(avatar_url, upload_path)
      avatar = filename
    else:
      avatar = '`default_avatar.jpg`'
    register_info = {
      'username': info['login'],
      'id_string': id_string,
      'avatar': avatar
    }
    if info['email']:
      register_info['email']
    user = User(**register_info)
    try:
      db.session.add(user)
      db.session.commit()
    except:
      db.session.rollback()
      response = jsonify({ 'error': 'create user error', 'message': '创建用户失败，请重新登录' })
      response.status_code = 500
      return response
  token = user.generate_auth_token(3600 * 24 * 30)
  return jsonify({ 'token': token })

@api.route('/user_detail/', methods=['GET'])
def get_user_detail():
  user_id = request.args.get('id')
  user = User.query.get_or_404(user_id)
  if user:
    return jsonify(user.detail())
  return bad_request('未查询到相关用户信息', true)

@api.route('/change-username/', methods=['POST'])
@login_required()
def save_username():
  username = request.json.get('username')
  if not username:
    return bad_request('用户名长度应该在2~15个字符', True)
  name_len = len(username)
  if name_len < 2 or name_len > 15:
    return bad_request('用户名长度应该在2~15个字符', True)
  user = User.query.filter_by(username=username).first()
  if user:
    if user.id == g.current_user.id:
      return bad_request('未修改用户名', True)
    return bad_request('该用户名已被占用', True)
  g.current_user.username = username
  try:
    db.session.add(g.current_user)
    db.session.commit()
    return jsonify({ 'message': '修改成功' })
  except:
    db.session.rollback()
    return bad_request('请求数据库出错，请重试', True)