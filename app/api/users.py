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
  access_token = access_data['access_token']
  req2 = urllib.request.Request('https://api.github.com/user?access_token='+access_token)
  html2 = urllib.request.urlopen(req2).read().decode('utf-8')
  info = json.loads(html2)
  return jsonify(info)

