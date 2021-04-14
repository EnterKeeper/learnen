from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_current_user

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
            user = get_current_user()
            if not ModeratorGroup.is_belong(user.group):
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
            user = get_current_user()
            if not AdminGroup.is_belong(user.group):
                raise errors.AccessDeniedError
            return func(*args, **kwargs)

        return decorator

    return wrapper
