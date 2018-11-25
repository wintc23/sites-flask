import os
import sys
import uuid
from flask import g, jsonify, request, send_from_directory
from . import api
from .decorators import login_required
from .errors import unauthorized, forbidden

@api.route('/save-image/', methods=['PUT'])
@login_required()
def save_image():
  img_url = None
  f = request.files['image']
  filename = str(uuid.uuid1()) + f.filename
  dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
  upload_path = dirname + '../files/'
  f.save(upload_path + filename)
  return jsonify({ 'message': '上传成功', 'filename': filename })

@api.route('/get-file/', methods = ['GET'])
def get_file():
  dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
  dirpath = dirname + '../files/'
  filename = request.args.get('filename')
  return send_from_directory(dirpath, filename)