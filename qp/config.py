class Config:
    SECRET_KEY = "VeryLongSecretString"
    JWT_SECRET_KEY = "VeryLongSecretString"
    PROPAGATE_EXCEPTIONS = True
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = False

    MAIL_SERVER = "smtp.yandex.ru"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "noreply@quick-polls.xyz"
    MAIL_DEFAULT_SENDER = ("Quick Polls", MAIL_USERNAME)
    MAIL_PASSWORD = "MailPassword"
