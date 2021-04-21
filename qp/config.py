class Config:
    SECRET_KEY = "Long secret string"
    JWT_SECRET_KEY = "Long secret string"
    PROPAGATE_EXCEPTIONS = True
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_CHECK_FORM = False
    JWT_ACCESS_TOKEN_EXPIRES = False
