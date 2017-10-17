from django.apps import AppConfig


class {{ cookiecutter.app_name|capitalize }}Config(AppConfig):
    name = '{{ cookiecutter.app_name }}'
