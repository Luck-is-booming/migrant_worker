import os
import sys
from pathlib import Path

import dj_database_url
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TEMPLATES_DIR = BASE_DIR / "templates"

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-local-key-for-dev-safety")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "anymail",

    "cloudinary_storage",
    "cloudinary",

    "core.apps.CoreConfig",
    "blog.apps.BlogConfig",
    "payments.apps.PaymentsConfig",
    "members.apps.MembersConfig",
    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "migrantcenter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "migrantcenter.wsgi.application"

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
USE_SQLITE = os.getenv("USE_SQLITE", "False") == "True"

if DATABASE_URL and not USE_SQLITE:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# Language / Time
LANGUAGE_CODE = "ne"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ne", _("Nepali")),
    ("en", _("English")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# Manual QR Payment Settings
MANUAL_PAYMENT_CONFIG = {
    "GENERAL_MEMBER_AMOUNT": os.getenv("GENERAL_MEMBER_AMOUNT", "500"),
    "LIFE_MEMBER_AMOUNT": os.getenv("LIFE_MEMBER_AMOUNT", "5000"),
}


# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Put your QR image here:
# static/images/payment_qr.jpg
STATICFILES_DIRS = [
    BASE_DIR / "static",
] if (BASE_DIR / "static").exists() else []


# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Cloudinary media storage
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL:
    CLOUDINARY_STORAGE = {
        "CLOUDINARY_URL": CLOUDINARY_URL,
    }

    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.StaticFilesStorage",
        },
    }


# Email
# In production, set RESEND_API_KEY and use a sender on a verified Resend domain.
# Without an API key, Django prints emails to the local console instead of failing.
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()

ANYMAIL = {
    "RESEND_API_KEY": RESEND_API_KEY,
}

EMAIL_BACKEND = (
    "anymail.backends.resend.EmailBackend"
    if RESEND_API_KEY
    else "django.core.mail.backends.console.EmailBackend"
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "MRN Ilam <onboarding@resend.dev>",
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMIN_NOTIFICATION_EMAIL = os.getenv(
    "ADMIN_NOTIFICATION_EMAIL",
    "info@mrnilam.org.np",
)
SITE_URL = os.getenv("SITE_URL", "https://mrnilam.org.np").rstrip("/")
EMAIL_NOTIFICATIONS_ENABLED = (
    os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "True").lower() == "true"
)


# Render / HTTPS proxy support
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Test environment
# Tests must never connect to Neon, Cloudinary, or Resend.
IS_TESTING = "test" in sys.argv

if IS_TESTING:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.memory.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    EMAIL_NOTIFICATIONS_ENABLED = False