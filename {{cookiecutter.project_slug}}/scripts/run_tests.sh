#!/bin/bash
{% if cookiecutter.virtualization_tool == 'drifter' %}

# don't delete this line, or copy that content and adjust it
. ./virtualization/drifter/ci/test-header.sh
{% endif %}

set -e

./scripts/check_migrations.sh

pytest "${@:-{{ cookiecutter.project_slug }}}"

flake8 {{ cookiecutter.project_slug }} fabfile.py
