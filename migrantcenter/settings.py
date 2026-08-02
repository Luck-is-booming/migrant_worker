import os
import sys
from pathlib import Path

import dj_database_url
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TEMPLATES_DIR = BASE_DIR / "templates"
IS_TESTING = "test" in sys.argv
DEBUG = os.getenv("DEBUG", "False").casefold() == "true"
USE_SQLITE = os.getenv("USE_SQLITE", "False").casefold() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "").strip()
IS_PRODUCTION = not DEBUG and bool(DATABASE_URL) and not USE_SQLITE and not IS_TESTING

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("SECRET_KEY is required in production.")
    SECRET_KEY = "development-only-secret-key-change-me"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,mrnilam.org.np,www.mrnilam.org.np",
    ).split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://mrnilam.org.np,https://www.mrnilam.org.np",
    ).split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "migrantcenter.apps.MRNAdminConfig",
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
    "counseling.apps.CounselingConfig",
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
    "migrantcenter.middleware.AdminLoginRateLimitMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "migrantcenter.middleware.SecurityHeadersMiddleware",
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
                "core.context_processors.public_site_settings",
            ],
        },
    },
]
WSGI_APPLICATION = "migrantcenter.wsgi.application"

if IS_TESTING and TEST_DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=TEST_DATABASE_URL,
            conn_max_age=0,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
elif IS_TESTING:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
elif DATABASE_URL and not USE_SQLITE:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=60,
            conn_health_checks=True,
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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ne"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True
LANGUAGES = [("ne", _("Nepali")), ("en", _("English"))]
LOCALE_PATHS = [BASE_DIR / "locale"]

MANUAL_PAYMENT_CONFIG = {
    # Legacy environment fallback only. Public applications remain paused until
    # verified fees and an official QR are published through Django Admin.
    "GENERAL_MEMBER_AMOUNT": os.getenv("GENERAL_MEMBER_AMOUNT", "0"),
    "LIFE_MEMBER_AMOUNT": os.getenv("LIFE_MEMBER_AMOUNT", "0"),
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "").strip()

if IS_TESTING:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.memory.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
elif CLOUDINARY_URL:
    CLOUDINARY_STORAGE = {"CLOUDINARY_URL": CLOUDINARY_URL}
    STORAGES = {
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    }

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024
COUNSELING_ATTACHMENTS_ENABLED = os.getenv("COUNSELING_ATTACHMENTS_ENABLED", "False").casefold() == "true"
COUNSELING_RATE_LIMIT_PER_HOUR = int(os.getenv("COUNSELING_RATE_LIMIT_PER_HOUR", "5"))
PRIVACY_RETENTION_PERIOD = os.getenv(
    "PRIVACY_RETENTION_PERIOD",
    "12 months after case closure unless a legal or audit obligation requires longer retention",
)
MEMBERSHIP_PAYMENT_PURPOSE = os.getenv(
    "MEMBERSHIP_PAYMENT_PURPOSE", "MRN Ilam organization membership fee"
)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
ANYMAIL = {"RESEND_API_KEY": RESEND_API_KEY}
if IS_TESTING:
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
elif RESEND_API_KEY:
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "MRN Ilam <onboarding@resend.dev>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMIN_NOTIFICATION_EMAIL = os.getenv("ADMIN_NOTIFICATION_EMAIL", "").strip()
EMAIL_NOTIFICATIONS_ENABLED = (
    os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "False").casefold() == "true"
    and not IS_TESTING
)
SITE_URL = os.getenv("SITE_URL", "https://mrnilam.org.np").rstrip("/")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mrn-ilam-local-cache",
        "TIMEOUT": 300,
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = IS_PRODUCTION
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
HSTS_ENABLED = os.getenv("HSTS_ENABLED", "False").casefold() == "true"
SECURE_HSTS_SECONDS = 31536000 if IS_PRODUCTION and HSTS_ENABLED else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION and HSTS_ENABLED
SECURE_HSTS_PRELOAD = IS_PRODUCTION and HSTS_ENABLED
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "members.importing": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
