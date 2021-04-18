from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, current_user

from . import errors
from ..models.users import ModeratorGroup, AdminGroup


def guest_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                pass
            return func(*args, **kwargs)

        return decorator

    return wrapper


def user_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                raise errors.NoAuthError
            if current_user.banned:
                raise errors.UserBannedError
            return func(*args, **kwargs)

        return decorator

    return wrapper


def moderator_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                raise errors.NoAuthError
            if current_user.banned:
                raise errors.UserBannedError
            if not ModeratorGroup.is_belong(current_user.group):
                raise errors.AccessDeniedError
            return func(*args, **kwargs)

        return decorator

    return wrapper


def admin_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                raise errors.NoAuthError
            if current_user.banned:
                raise errors.UserBannedError
            if not AdminGroup.is_belong(current_user.group):
                raise errors.AccessDeniedError
            return func(*args, **kwargs)

        return decorator

    return wrapper
