import dj_email_url

from . import get_env_variable
from .base import *  # noqa

DEBUG = bool(get_env_variable('DEBUG', True))
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
MIDDLEWARE_CLASSES += (  # noqa
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

SECRET_KEY = 'notsosecret'
INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS += (  # noqa
    'debug_toolbar',
    'django_extensions',
)

TEMPLATES[0]['OPTIONS']['loaders'] = (  # noqa
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

LOGGING = {}

EMAIL_URL = get_env_variable('EMAIL_URL', 'console://')
email_config = dj_email_url.parse(EMAIL_URL)
EMAIL_FILE_PATH = email_config['EMAIL_FILE_PATH']
EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
EMAIL_HOST = email_config['EMAIL_HOST']
EMAIL_PORT = email_config['EMAIL_PORT']
EMAIL_BACKEND = email_config['EMAIL_BACKEND']
EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
EMAIL_USE_SSL = email_config['EMAIL_USE_SSL']
