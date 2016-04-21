"""
Django settings for erudit project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from pathlib import Path

from celery.schedules import crontab

DEBUG = True
COMPRESS_ENABLED = True

BASE_DIR = Path(__file__)
ROOT_DIR = BASE_DIR.parents[3]

STATIC_ROOT = str(ROOT_DIR / 'static')
MEDIA_ROOT = str(ROOT_DIR / 'media')
UPLOAD_ROOT = str(ROOT_DIR / 'media' / 'uploads')

# URL of the admin page
ADMIN_URL = 'admin/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

SECRET_KEY = 'INSECURE'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    # Érudit apps
    'base',
    'erudit',
    'apps.public.book',
    'apps.public.citations',
    'apps.public.journal',
    'apps.public.search',
    'apps.public.thesis',
    'apps.userspace',
    'apps.userspace.journal',
    'apps.userspace.journal.authorization',
    'apps.userspace.journal.editor',
    'apps.userspace.journal.information',
    'apps.userspace.journal.subscription',
    'apps.userspace.reporting',
    'core.authorization',
    'core.account_actions',
    'core.accounts',
    'core.citations',
    'core.editor',
    'core.journal',
    'core.reporting',
    'core.subscription',

    # Third-party apps
    'grappelli',
    'modeltranslation',
    'post_office',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Third-party apps
    'crispy_forms',
    'django_select2',
    'datetimewidget',
    'plupload',
    'django_filters',
    'spurl',
    'rules',
    'ckeditor',
    'raven.contrib.django.raven_compat',
    'django_fsm',
    'easy_pjax',
    'django_js_reverse',
    'rest_framework',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zenon',
        'USER': 'postgres',
        'HOST': 'localhost',
    },
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    str(ROOT_DIR / 'erudit' / 'static' / 'build'),
    str(ROOT_DIR / 'erudit' / 'static'),
)


CRISPY_TEMPLATE_PACK = 'bootstrap3'
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'core.subscription.middleware.SubscriptionMiddleware',
    'core.citations.middleware.SavedCitationListMiddleware',
)

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(ROOT_DIR / 'erudit' / 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'base.context_processors.common_settings',
            ],
        },
    },
]


LOGIN_URL = 'public:auth:login'

# Database configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

# Put this in settings.py
POST_OFFICE = {
    'DEFAULT_PRIORITY': 'now',
}

EMAIL_BACKEND = 'post_office.EmailBackend'
EMAIL_HOST = "mail"
EMAIL_PORT = '25'
RENEWAL_FROM_EMAIL = 'admin@localhost'

DEFAULT_FROM_EMAIL = 'ne-pas-repondre@erudit.org'
TECH_EMAIL = 'tech@erudit.org'
PUBLISHER_EMAIL = 'edition@erudit.org'
COMMUNICATION_EMAIL = 'media@erudit.org'
SUBSCRIPTION_EMAIL = 'client@erudit.org'

WSGI_APPLICATION = 'erudit.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr'

LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English'),
)

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'core.accounts.backends.EmailBackend',
    'core.accounts.backends.MandragoreBackend',
    'core.accounts.backends.AbonnementIndividuelBackend',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

INDIVIDUAL_SUBSCRIPTION_SALT = 'sample salt'

# Fedora settings
FEDORA_ROOT = 'http://10.1.1.33:8080/fedora'
FEDORA_USER = 'fcAdmin'
FEDORA_PASSWORD = 'fcAdmin'

SOLR_ROOT = 'http://10.1.1.33:8080/solr/eruditpersee/'
SOLR_ADMIN = 'http://10.1.1.33:8080/solr/admin/cores/'

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Raven settings
RAVEN_CONFIG = {
    'dsn': None,
}

# Celery settings
# -----------------------------------

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'EST'
CELERY_TASK_RESULT_EXPIRES = None

CELERYBEAT_SCHEDULE = {
    'issuesubmission-files-removal': {
        'task': 'core.editor.tasks.handle_issuesubmission_files_removal',
        'schedule': crontab(minute=0, hour=0),  # Executed daily at midnight
    },
}

# DRF settings
# -----------------------------------

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend', ),
}

# MailChimp settings
# -----------------------------------

MAILCHIMP_UUID = ""
MAILCHIMP_ACTION_URL = ""


# Django JS reverse settings
# -----------------------------------

JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['public:citations', ]


try:
    from .settings_env import *  # noqa
except ImportError:
    pass

try:
    from ..settings_env import *  # noqa
except ImportError:
    pass
