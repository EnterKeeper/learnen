from functools import wraps

from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

from data import api_errors


def api_jwt_required():
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
