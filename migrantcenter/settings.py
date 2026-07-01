import os
from pathlib import Path

import dj_database_url
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TEMPLATES_DIR = BASE_DIR / 'templates'

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-local-key-for-dev-safety")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary_storage',
    'cloudinary',

    'core.apps.CoreConfig',
    'blog.apps.BlogConfig',
    'payments.apps.PaymentsConfig',
    'members.apps.MembersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'migrantcenter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'migrantcenter.wsgi.application'

if os.getenv("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ne'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ne', _('Nepali')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

ESEWA_CONFIG = {
    "MERCHANT_ID": os.getenv("ESEWA_MERCHANT_ID", "EPAYTEST"),
    "SECRET_KEY": os.getenv("ESEWA_SECRET_KEY", "8gBm/:&EnhH.1/q"),
    "INITIATE_URL": os.getenv(
        "ESEWA_INITIATE_URL",
        "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
    ),
    "GENERAL_MEMBER_AMOUNT": os.getenv("ESEWA_GENERAL_AMOUNT", "500"),
    "LIFE_MEMBER_AMOUNT": os.getenv("ESEWA_LIFE_AMOUNT", "5000"),
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
CLOUDINARY_STORAGE = {
    'CLOUDINARY_URL': CLOUDINARY_URL,
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DEFAULT_FROM_EMAIL = "MWRWPC Portal <onboarding@resend.dev>"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'