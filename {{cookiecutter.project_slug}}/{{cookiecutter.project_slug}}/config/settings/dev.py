from . import get_env_variable
from .base import *  # noqa

DEBUG = bool(get_env_variable("DEBUG", True))
DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_COLLAPSED": True,
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}
MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)  # noqa

SECRET_KEY = "notsosecret"
INTERNAL_IPS = ("127.0.0.1",)

INSTALLED_APPS += ("debug_toolbar", "django_extensions")  # noqa

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DJANGO_VITE_DEV_MODE = bool(int(get_env_variable("DJANGO_VITE_DEV_MODE", True)))
