import environ
import logging
import structlog
from pathlib import Path

from sentry_sdk.integrations.logging import LoggingIntegration
from structlog.stdlib import LoggerFactory

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parents[2]

env = environ.Env(
    DEBUG=(bool, False),
    EXPOSE_OPENMETRICS=(bool, False),
    SENTRY_ENVIRONMENT=(str, 'default'),
    SECRET_KEY=(str, None),
    ADMIN_URL=(str, 'admin/'),
    FALLBACK_BASE_URL=(str, 'http://retro.erudit.org/'),
    ALLOWED_HOSTS=(list, []),
    STATIC_ROOT=(str, str(ROOT_DIR / 'static')),
    MEDIA_ROOT=(str, str(ROOT_DIR / 'media')),
    STATIC_URL=(str, '/static/'),
    MEDIA_URL=(str, '/media/'),
    UPLOAD_ROOT=(str, str(ROOT_DIR / 'media' / 'uploads')),
    MANAGED_COLLECTIONS=(list, ['erudit', 'unb']),

    MAIN_DATABASE_URL=(str, 'mysql://root@localhost/eruditorg'),
    RESTRICTION_DATABASE_URL=(str, 'mysql://root@localhost/restriction'),

    CACHE_URL=(str, 'locmemcache://'),
    FILEBASED_CACHE_DIRECTORY=(str, '/tmp'),
    FILEBASED_CACHE_TIMEOUT=(int, 300),
    FILEBASED_CACHE_SHARDS=(int, 8),
    FILEBASED_CACHE_DATABASE_TIMEOUT=(float, 0.01),
    FILEBASED_CACHE_SIZE_LIMIT=(int, 8),
    ERUDIT_FEDORA_XML_CONTENT_CACHE_TIMEOUT=(int, 3600),
    EMAIL_HOST=(str, None),
    EMAIL_PORT=(int, 25),
    EMAIL_HOST_USER=(str, None),
    EMAIL_HOST_PASSWORD=(str, None),

    MAILCHIMP_UUID=(str, None),
    MAILCHIMP_ACTION_URL=(str, None),

    DEFAULT_FROM_EMAIL=(str, 'info@erudit.org'),
    DEBUG_EMAIL_ADDRESS=(str, 'info@erudit.org'),

    FEDORA_ROOT=(str, None),
    FEDORA_USER=(str, None),
    FEDORA_PASSWORD=(str, None),

    SOLR_ROOT=(str, None),

    VICTOR_SOAP_URL=(str, None),
    VICTOR_SOAP_USERNAME=(str, None),
    VICTOR_SOAP_PASSWORD=(str, None),

    ERUDIT_OCLC_BACKEND_URL=(str, None),
    ERUDIT_KBART_BACKEND_URL=(str, None),
    ERUDIT_KBART_2014_BACKEND_URL=(str, None),

    Z3950_HOST=(str, None),
    Z3950_PORT=(int, None),
    Z3950_DATABASE=(str, None),

    SUSHI_URL=(str, None),

    ERUDIT_COUNTER_BACKEND_URL=(str, None),

    SUBSCRIPTION_EXPORTS_ROOT=(str, None),
    BOOKS_DIRECTORY=(str, None),
    RESTRICTION_ABONNE_ICONS_PATH=(str, None),
    EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER=(str, None),
    SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS=(int, 12),
    CULTURAL_JOURNAL_EMBARGO_IN_MONTHS=(int, 36),

    DJANGO_LOG_DIRECTORY=(str, None),
    RAVEN_DSN=(str, None),

    FIXTURE_ROOT=(str, None),
    JOURNAL_FIXTURES=(str, None),

    ANALYTICS_HOTJAR_TRACKING_CODE=(str, None),
    ANALYTICS_GOOGLE_TRACKING_CODE=(str, None),

    GOOGLE_CASA_KEY=(str, None),

    REDIS_HOST=(str, None),
    REDIS_PORT=(int, None),
    REDIS_INDEX=(int, None),
)
environ.Env.read_env(str(ROOT_DIR / '.env'))

# General configuration
# -----------------------------------------------------------------------------

ALLOWED_HOSTS = env('ALLOWED_HOSTS')
INTERNAL_IPS = ('127.0.0.1',)
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ADMIN_URL = env('ADMIN_URL')
FALLBACK_BASE_URL = env('FALLBACK_BASE_URL')
MANAGED_COLLECTIONS = env('MANAGED_COLLECTIONS')

# Static and media files
# -----------------------------------------------------------------------------

STATIC_ROOT = env('STATIC_ROOT')
MEDIA_ROOT = env('MEDIA_ROOT')
UPLOAD_ROOT = env('UPLOAD_ROOT')
STATIC_URL = env('STATIC_URL')
MEDIA_URL = env('MEDIA_URL')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    str(ROOT_DIR / 'eruditorg' / 'static' / 'build'),
    str(ROOT_DIR / 'eruditorg' / 'static'),
)

# Initialize sentry
# -----------------------------------------------------------------------------


RAVEN_DSN = env('RAVEN_DSN')
if RAVEN_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.WARNING  # Send errors as events
    )
    sentry_sdk.init(
        dsn=RAVEN_DSN,
        integrations=[sentry_logging, DjangoIntegration()],
        environment=env("SENTRY_ENVIRONMENT")
    )


# Application definition
# -----------------------------------------------------------------------------

EXPOSE_OPENMETRICS = env("EXPOSE_OPENMETRICS")

INSTALLED_APPS = (
    # Érudit apps
    'base',
    'erudit',
    'apps.public.book',
    'apps.public.citations',
    'apps.public.journal',
    'apps.public.search',
    'apps.public.site_messages',
    'apps.public.thesis',
    'apps.userspace',
    'apps.userspace.journal',
    'apps.userspace.journal.authorization',
    'apps.userspace.journal.editor',
    'apps.userspace.journal.information',
    'apps.userspace.journal.subscription',
    'apps.userspace.library',
    'apps.userspace.library.authorization',
    'apps.userspace.library.members',
    'apps.userspace.library.stats',
    'apps.userspace.library.subscription_ips',
    'apps.userspace.reporting',
    'core.authorization',
    'core.accounts',
    'core.citations',
    'core.editor',
    'core.journal',
    'core.metrics',
    'core.reporting',
    'core.subscription',

    # Third-party apps
    'modeltranslation',
    'polymorphic',
    'post_office',
    'taggit',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Third-party apps
    'eruditarticle',
    'waffle',
    'account_actions',
    'resumable_uploads',
    'rules',
    'ckeditor',
    'django_fsm',
    'easy_pjax',
    'django_js_reverse',
    'widget_tweaks',
    'rangefilter',
    'adv_cache_tag',
    'reversion',
    'reversion_compare',
)

ADD_REVERSION_ADMIN = True

if EXPOSE_OPENMETRICS:
    INSTALLED_APPS = INSTALLED_APPS + ('django_prometheus', )

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'base.middleware.LanguageCookieMiddleware',
    'core.subscription.middleware.SubscriptionMiddleware',
    'core.citations.middleware.SavedCitationListMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'base.middleware.RedirectToFallbackMiddleware',
    'base.middleware.PolyglotLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
)

if EXPOSE_OPENMETRICS:
    MIDDLEWARE = (
        ('django_prometheus.middleware.PrometheusBeforeMiddleware',) +
        MIDDLEWARE +
        ('django_prometheus.middleware.PrometheusAfterMiddleware',)
    )

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(ROOT_DIR / 'eruditorg' / 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'base.context_processors.cache_constants',
                'base.context_processors.common_settings',
                'apps.public.site_messages.context_processors.active_site_messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'builtins': [
                'easy_pjax.templatetags.pjax_tags',
            ],
        },
    },
]

LOGIN_URL = 'public:auth:login'
LOGIN_REDIRECT_URL = 'public:home'


# Databases
# -----------------------------------------------------------------------------

DATABASES = {
    'default': env.db('MAIN_DATABASE_URL'),
    'restriction': env.db('RESTRICTION_DATABASE_URL'),
}

DATABASE_ROUTERS = [
    'core.subscription.restriction.router.RestrictionRouter',
]


# Cache
# -----------------------------------------------------------------------------

CACHES = {
    'default': env.cache("CACHE_URL"),
    'files': {
        'BACKEND': 'diskcache.DjangoCache',
        'LOCATION': env('FILEBASED_CACHE_DIRECTORY'),
        'TIMEOUT': env('FILEBASED_CACHE_TIMEOUT'),  # TTL of cached content
        'SHARDS': env('FILEBASED_CACHE_SHARDS'),
        'DATABASE_TIMEOUT': env('FILEBASED_CACHE_DATABASE_TIMEOUT'),  # Timeout for database access
        'OPTIONS': {
            'size_limit': env('FILEBASED_CACHE_SIZE_LIMIT'),
        },
    },
}
NEVER_TTL = 0               # Do not cache
SHORT_TTL = 60 * 60         # Cache for 1 hour
LONG_TTL = 60 * 60 * 24     # Cache for 1 day
FOREVER_TTL = None          # Cache forever

# django-adv-cache-tag settings
# -----------------------------------------------------------------------------
# The first argument of the cache tag (after the fragment's name) will be used
# as a primary key in the cache key.
ADV_CACHE_INCLUDE_PK = True
# The last argument of the cache tag will be used as the cache version in the
# cache content (not the key). This means that the cache key will not change,
# but the cache content will be invalidated if the version change.
ADV_CACHE_VERSIONING = True
# Compress the cache content with zlib.
ADV_CACHE_COMPRESS = True

ERUDIT_FEDORA_XML_CONTENT_CACHE_TIMEOUT = env("ERUDIT_FEDORA_XML_CONTENT_CACHE_TIMEOUT")

# Emails
# -----------------------------------------------------------------------------

POST_OFFICE = {
    'BATCH_SIZE': 25,
}

EMAIL_BACKEND = 'post_office.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# Addresses
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
DEBUG_EMAIL_ADDRESS = env('DEBUG_EMAIL_ADDRESS')

TECH_EMAIL = 'tech@erudit.org'
PUBLISHER_EMAIL = 'edition@erudit.org'
COMMUNICATION_EMAIL = 'media@erudit.org'
SUBSCRIPTION_EMAIL = 'client@erudit.org'
ACCOUNT_EMAIL = 'comptes@erudit.org'

# Internationalisation
# -----------------------------------------------------------------------------

LANGUAGE_CODE = 'fr'

LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English'),
)

TIME_ZONE = 'America/Toronto'

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = (
    str(ROOT_DIR / 'locale'),
)

USE_TZ = True

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'core.accounts.backends.EmailBackend',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
]

# External systems
# -----------------------------------------------------------------------------

# Fedora settings
FEDORA_ROOT = env('FEDORA_ROOT')
FEDORA_USER = env('FEDORA_USER')
FEDORA_PASSWORD = env('FEDORA_PASSWORD')

# Solr settings
SOLR_ROOT = env('SOLR_ROOT')
SOLR_TIMEOUT = 10

# Victor settings
VICTOR_SOAP_URL = env('VICTOR_SOAP_URL')
VICTOR_SOAP_USERNAME = env('VICTOR_SOAP_USERNAME')
VICTOR_SOAP_PASSWORD = env('VICTOR_SOAP_PASSWORD')

# KBART
ERUDIT_KBART_BACKEND_URL = env('ERUDIT_KBART_BACKEND_URL')
ERUDIT_KBART_2014_BACKEND_URL = env('ERUDIT_KBART_2014_BACKEND_URL')
ERUDIT_OCLC_BACKEND_URL = env('ERUDIT_OCLC_BACKEND_URL')

# Journal providers
ERUDIT_JOURNAL_PROVIDERS = {
    'fedora': [
        {
            'collection_title': 'Érudit',
            'collection_code': 'erudit',
            'localidentifier': 'erudit',
        },
        {
            'collection_title': 'The Electronic Text Centre at UNB Libraries',
            'collection_code': 'unb',
            'localidentifier': 'unb',
        },
    ],
    'oai': [
        {
            'collection_title': 'Persée',
            'collection_code': 'persee',
            'endpoint': 'http://oai.persee.fr/oai',
            'issue_metadataprefix': 'persee_mets',
        },
    ],
}

SUSHI_URL = env("SUSHI_URL")
Z3950_HOST = env("Z3950_HOST")
Z3950_PORT = env("Z3950_PORT")
Z3950_DATABASE = env("Z3950_DATABASE")

ERUDIT_COUNTER_BACKEND_URL = env("ERUDIT_COUNTER_BACKEND_URL")


# Metrics and analytics
# -----------------------------------------------------------------------------
METRICS_ACTIVATED = False
# METRICS_INFLUXDB_HOST = env("METRICS_INFLUXDB_HOST", default='localhost')
# METRICS_INFLUXDB_PORT = env("METRICS_INFLUXDB_PORT", default=0)
# METRICS_INFLUXDB_DBNAME = env("METRICS_INFLUXDB_DBNAME", default="db")
# METRICS_INFLUXDB_USER = env("METRICS_INFLUXDB_USER", default="db")
# METRICS_INFLUXDB_PASSWORD = env("METRICS_INFLUXDB_PASSWORD", default="password")

# Paths
# -----------------------------------------------------------------------------

SUBSCRIPTION_EXPORTS_ROOT = env('SUBSCRIPTION_EXPORTS_ROOT')
BOOKS_DIRECTORY = env('BOOKS_DIRECTORY')

# Editor
# -----------------------------------------------------------------------------
EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER = env('EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER')

# Logging settings
# -----------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'handlers': {
        'referer': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': '/tmp/www.erudit.org.referer.log',
        },

        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'root': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'core.subscription.middleware': {
            'level': 'INFO',
            'handlers': ['referer', 'console', ],
            'propagate': False,
        },
    }
}

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[
        structlog.dev.ConsoleRenderer(),
    ]
)

# MailChimp settings
# -----------------------------------

MAILCHIMP_UUID = env('MAILCHIMP_UUID', default=None)
MAILCHIMP_ACTION_URL = env('MAILCHIMP_ACTION_URL', default=None)

# Embargo
# -----------------------------------------------------------------------------

SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS = env('SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS')
CULTURAL_JOURNAL_EMBARGO_IN_MONTHS = env('CULTURAL_JOURNAL_EMBARGO_IN_MONTHS')

# Django JS reverse settings
# -----------------------------------

JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['public:citations', 'public:search', ]

# Django-ckeditor settings
# -----------------------------------

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', 'Bold', 'Italic', 'Underline'],
            ['Image', 'NumberedList', 'BulletedList', '-', 'JustifyLeft',
             'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat']
        ]
    }
}

# Google CASA
# -----------
GOOGLE_CASA_KEY = env('GOOGLE_CASA_KEY')

# Redis
# -----
REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env('REDIS_PORT')
REDIS_INDEX = env('REDIS_INDEX')
