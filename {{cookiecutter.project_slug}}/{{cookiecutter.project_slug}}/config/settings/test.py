from .base import *  # noqa

SECRET_KEY = 'test'

DEBUG = False

# Always use local memory cache, don't bother trying memcached or similar
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable logging messages
LOGGING = {}
