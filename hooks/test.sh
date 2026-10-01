#!/usr/bin/env bash
set -euxvo pipefail

TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cd "$TMP_DIR"
uvx cookiecutter "$TEMPLATE_DIR" --no-input

PROJECT_DIR="$TMP_DIR/my_project"
cd "$PROJECT_DIR"

uv venv .venv
uv pip install --python .venv/bin/python -r requirements/dev.in

DATABASE_URL="sqlite:///db.sqlite3" .venv/bin/python manage.py check

echo "Cookiecutter generated project in $TMP_DIR passed Django checks"
