from functools import wraps
from flask import g
from .errors import forbidden
from ..models import Permission

def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorator_func(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('insufficient permissions')
            return func(*args, **kwargs)
        return decorator_func
    return decorator

