import os

from django.utils.translation import gettext_lazy as _

import dj_database_url
import dj_email_url

from .. import get_project_root_path
from . import get_env_variable

gettext = lambda s: s

# Full filesystem path to the project.
BASE_DIR = get_project_root_path()

# Internationalization
LANGUAGE_CODE = "{{ cookiecutter.default_language }}"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
{%- for lang in cookiecutter.language_list.split(',') %}
    ("{{ lang }}", _("{{ lang }}")),
{%- endfor %}
)

LOCALE_PATHS = ("locale/",)

# A boolean that turns on/off debug mode. When set to ``True``, stack traces
# are displayed for error pages. Should always be set to ``False`` in
# production. Best set to ``True`` in dev.py
DEBUG = False

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ("127.0.0.1",)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# The numeric mode to set newly-uploaded files to. The value should be
# a mode you'd pass directly to os.chmod.
FILE_UPLOAD_PERMISSIONS = 0o644

ALLOWED_HOSTS = tuple(get_env_variable("ALLOWED_HOSTS", "").splitlines())

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

USE_X_FORWARDED_HOST = get_env_variable("USE_X_FORWARDED_HOST", False)

SECRET_KEY = get_env_variable("SECRET_KEY", "")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher"
]


#############
# DATABASES #
#############

DATABASES = {"default": dj_database_url.parse(get_env_variable("DATABASE_URL"))}

# Allow using a separate password, from a k8s secret, for example
DATABASE_PASSWORD = get_env_variable('DATABASE_PASSWORD', False)
if DATABASE_PASSWORD:
    DATABASES['default']['PASSWORD'] = DATABASE_PASSWORD

#########
# PATHS #
#########

# Name of the directory for the project.
PROJECT_DIRNAME = "{{ cookiecutter.project_slug }}"

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIRNAME

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = get_env_variable("STATIC_URL", "/static/")

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# This is usually not used in a dev env, hence the default value
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = get_env_variable("STATIC_ROOT", "/tmp/static")

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = get_env_variable("MEDIA_URL", "/media/")

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = get_env_variable("MEDIA_ROOT", "/tmp/static/media")

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = "%s.config.urls" % PROJECT_DIRNAME
WSGI_APPLICATION = "{{ cookiecutter.project_slug }}.config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "{{ cookiecutter.project_slug }}", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.template.context_processors.csrf",
                "django.template.context_processors.tz",
                "django.template.context_processors.static",
            ]
        },
    }
]


################
# APPLICATIONS #
################

INSTALLED_APPS = (
    "{{ cookiecutter.project_slug }}.core.apps.CoreConfig",
    {% if cookiecutter.override_user_model == 'y' -%}
    "{{ cookiecutter.project_slug }}.accounts.apps.AccountsConfig",
    {% endif -%}
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "django.contrib.messages",
)

# List of middleware classes to use. Order is important; in the request phase,
# these middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)


{% if cookiecutter.override_user_model == 'y' -%}
##################
# AUTHENTICATION #
##################
AUTH_USER_MODEL = "accounts.User"


{% endif -%}


###########
# LOGGING #
###########

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler"}},
    "loggers": {"": {"handlers": ["console"], "level": "ERROR", "propagate": True}},
}


#############
# E-Mailing #
#############
EMAIL_URL = get_env_variable("EMAIL_URL", "console://")
email_config = dj_email_url.parse(EMAIL_URL)
EMAIL_FILE_PATH = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL = email_config["EMAIL_USE_SSL"]
DEFAULT_FROM_EMAIL = get_env_variable("EMAIL_FROM", "webmaster@localhost")
