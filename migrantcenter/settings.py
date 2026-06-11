import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
import dj_database_url # 🚨 NEW: Added database string parsing utility

# Load .env first (VERY IMPORTANT)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TEMPLATES_DIR = BASE_DIR / 'templates'

# ========================
# SECURITY SETTINGS
# ========================
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-local-key-for-dev-safety")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ['*']

# ========================
# APPLICATIONS
# ========================
INSTALLED_APPS = [
    # cloudinary_storage MUST come before django.contrib.staticfiles
    'cloudinary_storage',
    'cloudinary',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core.apps.CoreConfig',
    'blog.apps.BlogConfig',
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # 🚨 NEW: Added for handling production admin assets securely
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'migrantcenter.urls'

# ========================
# TEMPLATES
# ========================
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

# ========================
# DATABASE (Hybrid Local/Neon Setup)
# ========================
# 🚨 UPDATED: Looks for Neon's environment string first. If it can't find it, falls back to your local SQLite file smoothly!
if os.getenv("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# INTERNATIONALIZATION
# ========================
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

# ========================
# STATIC FILES (Admin Styles Support)
# ========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ========================
# CLOUDINARY STORAGE
# ========================
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

CLOUDINARY_STORAGE = {
    'CLOUDINARY_URL': CLOUDINARY_URL
}

# 🚨 ADD THIS LINE BELOW TO FIX THE DEPRECATION ERROR
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
      
        "BACKEND": "whitenoise.storage.StaticFilesStorage", 
    },
}

# ========================
# EMAIL (RESEND)
# ========================
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DEFAULT_FROM_EMAIL = "MWRWPC Portal <onboarding@resend.dev>"

# ========================
# DEFAULT AUTO FIELD
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'