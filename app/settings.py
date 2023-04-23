import os

import sentry_sdk
from corsheaders.defaults import default_headers
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

from app.common.enums import EnvironmentOptions

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT_URLCONF = "app.urls"

load_dotenv(str(BASE_DIR) + "/.env", override=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("PROD") == None
ENVIRONMENT = (
    EnvironmentOptions.PRODUCTION
    if os.environ.get("PROD")
    else EnvironmentOptions.DEVELOPMENT
    if os.environ.get("DEV")
    else EnvironmentOptions.LOCAL
)

DOMAIN = "api.tihlde.org"
WEBSITE_URL = (
    "https://tihlde.org"
    if ENVIRONMENT == EnvironmentOptions.PRODUCTION
    else "https://dev.tihlde.org"
    if ENVIRONMENT == EnvironmentOptions.DEVELOPMENT
    else "http://localhost:3000"
)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "dry_rest_permissions",
    "polymorphic",
    # Our apps
    "app.common",
    "app.communication",
    "app.content",
    "app.group",
    "app.authentication",
    "app.util",
    "app.career",
    "app.forms",
    "app.gallery",
    "app.badge",
]

MIDDLEWARE = [
    # Django Cors Headers
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Base Middleware
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

# Django rest framework
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "EXCEPTION_HANDLER": "app.util.exceptions.exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Auth0 Authentication
AUTH_USER_MODEL = "content.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]

JWT_AUTH = {
    "JWT_PAYLOAD_GET_USERNAME_HANDLER": "app.authentication.utils.get_userid_from_decoded_jwt",
    "JWT_DECODE_HANDLER": "app.authentication.utils.decode_jwt",
    "JWT_ALGORITHM": "RS256",
    "JWT_AUDIENCE": "https://dev-api.tihlde.org",
    "JWT_ISSUER": "https://tihlde-dev.eu.auth0.com/",
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (
            # It is important that we load the base templates first
            os.path.join(PROJECT_ROOT, "./static", "templates"),
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
        },
    },
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
        "OPTIONS": {"charset": "utf8mb4", "use_unicode": True},
        "CONN_MAX_AGE": 60,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST") or "smtp.mailtrap.io"
EMAIL_PORT = os.environ.get("EMAIL_PORT") or "2525"
EMAIL_HOST_USER = os.environ.get("EMAIL_USER") or "75ecff025dcb39"
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD") or "8b1a00e838d6b7"

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "nb-no"
TIME_ZONE = "Europe/Oslo"
USE_I18N = True
USE_TZ = True

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow all host headers
ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/api/static/"

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = default_headers + ("X-CSRF-Token",)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "mysite.log",
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "propagate": True,
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["file"],
    },
}

CELERY_BROKER_URL = "amqp://guest:guest@rabbitmq:5672"
if ENVIRONMENT == EnvironmentOptions.LOCAL:
    CELERY_TASK_ALWAYS_EAGER = True

AZURE_BLOB_STORAGE_NAME = "tihldestorage.blob.core.windows.net"

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=ENVIRONMENT.value,
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # Adjusting this value in production is recommended,
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
