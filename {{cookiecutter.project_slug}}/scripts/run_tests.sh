#!/bin/bash

set -e

./scripts/check_migrations.sh

pytest "${@:-{{ cookiecutter.project_slug }}}"

flake8 {{ cookiecutter.project_slug }} fabfile.py
