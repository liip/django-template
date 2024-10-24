#!/bin/bash

set -e

./scripts/check_migrations.sh

pytest "${@:-{{ cookiecutter.project_slug }}}"

ruff check {{ cookiecutter.project_slug }} fabfile.py
