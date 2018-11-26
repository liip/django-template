from . import get_env_variable
from .base import *  # noqa

import django_heroku
django_heroku.settings(locals())

DEBUG = False
