from functools import wraps
from flask import g
from .errors import forbidden, unauthorized

def permission_required(permission):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if not g.current_user.can(permission):
        return forbidden('Insufficient permissions')
      return f(*args, **kwargs)
    return decorated_function
  return decorator

def login_required():
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if g.current_user.is_anonymous:
        return unauthorized('非法请求')
      return f(*args, **kwargs)
    return decorated_function
  return decorator
