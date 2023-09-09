"""
Django settings for CheckSystem project.

Generated by 'django-admin startproject' using Django 2.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import dotenv

# Load environment by loading path of file from environment
# dotenv.load_dotenv("/shared/.env.prod.secrets")
dotenv.load_dotenv(os.environ["DJANGO_ENV_PATH"])

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATE_DIRS = [
    os.path.join(PROJECT_PATH, "templates/"),
]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
APPEND_SLASH = True
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# Application definition

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")
CORS_ALLOWED_ORIGIN_REGEXES = []

# CORS_ORIGIN_ALLOW_ALL = True
INSTALLED_APPS = [
    "channels",
    "daphne",
    "corsheaders",
    "django_extensions",
    "django_q",
    "simple_history",
    "rest_framework",
    "coba.apps.CobaConfig",
    "ashkan.apps.AshkanConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

Q_CLUSTER = {
    "name": "coba_cluster",
    "workers": 1,
    "retry": 60 * 4,
    "max_attempts": 1,
    "timeout": 60 * 3,
    "orm": "default",
    "has_replica": True,
}

# EMAIL SETUP

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = "no.reply.calclab.weekly@utep.edu"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    #"coba.views.TemplateErrorMiddleware",
]

ROOT_URLCONF = "CheckSystem.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR + "/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}


WSGI_APPLICATION = "CheckSystem.wsgi.application"

# Channels settings
ASGI_APPLICATION = "CheckSystem.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        # 'BACKEND' : "channels_redis.core.RedisChannelLayer",
        # 'CONFIG' : {
        #     'hosts' : [('127.0.0.1',6379)]
        # },
        # option if want to use redis
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "MST7MDT"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
