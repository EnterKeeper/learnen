from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_current_user
from flask_jwt_extended.exceptions import NoAuthorizationError

from data import api_errors
from data.groups import ModeratorGroup, AdminGroup


def user_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except NoAuthorizationError:
                raise api_errors.NoAuthError
            return func(*args, **kwargs)

        return decorator

    return wrapper


def moderator_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except NoAuthorizationError:
                raise api_errors.NoAuthError
            user = get_current_user()
            if not ModeratorGroup.is_allowed(user.group):
                raise api_errors.AccessDeniedError
            return func(*args, **kwargs)

        return decorator

    return wrapper


def admin_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except NoAuthorizationError:
                raise api_errors.NoAuthError
            user = get_current_user()
            if not AdminGroup.is_allowed(user.group):
                raise api_errors.AccessDeniedError
            return func(*args, **kwargs)

        return decorator

    return wrapper
