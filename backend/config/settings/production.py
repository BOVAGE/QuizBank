from decouple import config

ALLOWED_HOSTS = ["quizzybankky.herokuapp.com", ".herokuapp.com"]

DATABASES = {
    "default": {
        "ENGINE": "django_psdb_engine",
        "NAME": config("DB_NAME"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "OPTIONS": {"ssl": {"ca": config("MYSQL_ATTR_SSL_CA")}, "charset": "utf8mb4"},
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# CELERY CONFIG
CELERY_BROKER_URL = config("REDIS_URL")
