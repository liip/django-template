from .base import *  # noqa

SECRET_KEY = "test"

DEBUG = False

# Always use local memory cache, don't bother trying memcached or similar
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# use basic password hashing for tests for better performance
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
