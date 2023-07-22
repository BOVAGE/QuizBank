from decouple import config

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        # "OPTIONS": {"charset": "utf8mb4"},
    }
}

# CORS
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:5500",]


# EMAIL SENDING CONFIG
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CELERY CONFIG
CELERY_BROKER_URL = config("CELERY_BROKER_URL")
