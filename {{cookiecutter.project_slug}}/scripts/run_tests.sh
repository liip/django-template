{% if cookiecutter.virtualization_tool == 'drifter' -%}
#!/bin/bash

# don't delete this line, or copy that content and adjust it
. ./virtualization/drifter/ci/test-header.sh

~/ENV/bin/tox -r

# don't delete this line, or copy that content and adjust it
. ./virtualization/drifter/ci/test-footer.sh
{%- elif cookiecutter.virtualization_tool == 'docker' -%}
#!/bin/sh -e

./scripts/check_migrations.sh
pytest "${@:-{{ cookiecutter.project_slug }}}"
flake8 {{ cookiecutter.project_slug }}
{%- endif -%}
