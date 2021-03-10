from . import get_env_variable
from .base import *  # noqa

DEBUG = bool(get_env_variable("DEBUG", True))
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)  # noqa

SECRET_KEY = "notsosecret"
INTERNAL_IPS = ("127.0.0.1",)

INSTALLED_APPS += (  # noqa
    "debug_toolbar",
    "django_extensions",
    "rosetta"
)

TEMPLATES[0]["OPTIONS"]["loaders"] = (  # noqa
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

LOGGING = {}
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
