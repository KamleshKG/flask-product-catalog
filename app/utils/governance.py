from functools import wraps
from flask import abort, current_app, request
from flask_login import current_user
import json
from datetime import datetime

class Permission:
    READ = 0x01
    CREATE = 0x02
    UPDATE = 0x04
    DELETE = 0x08
    ADMIN = 0x80

PERMISSIONS = {
    'product:read': Permission.READ,
    'product:create': Permission.CREATE,
    'product:update': Permission.UPDATE,
    'product:delete': Permission.DELETE,
    'user:manage': Permission.ADMIN
}

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(PERMISSIONS[permission_name]):
                current_app.logger.warning(
                    f"Permission denied for {current_user.id} "
                    f"attempting {permission_name}"
                )
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required('user:manage')(f)