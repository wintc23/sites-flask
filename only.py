from flask import jsonify

def res_json(data, code = 0, msg = ''):
  # code:
  #   0 正常返回
  #   -1 无权限，客户端跳转到登录界面
  res = {
    'data': data,
    'code': code,
    'msg': msg
  }
  return jsonify(res)