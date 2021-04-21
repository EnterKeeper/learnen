class Config:
    SECRET_KEY = "VeryLongSecretString"
    JWT_SECRET_KEY = "VeryLongSecretString"
    PROPAGATE_EXCEPTIONS = True
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True

