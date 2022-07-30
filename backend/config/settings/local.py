from decouple import config

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django_psdb_engine",
        "NAME": config("DB_NAME"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

# EMAIL SENDING CONFIG
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
