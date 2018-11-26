"""
WSGI config for {{ cookiecutter.project_slug }} project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from {{ cookiecutter.project_slug }}.config import get_project_root_path, import_env_vars

import_env_vars(os.path.join(get_project_root_path(), 'envdir'))

{% set config_name = 'heroku' if cookiecutter.setup_heroku == 'y' else 'base' %}
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ cookiecutter.project_slug }}.config.settings.{{ config_name }}")


application = get_wsgi_application()
