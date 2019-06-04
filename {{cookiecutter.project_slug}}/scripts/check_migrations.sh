#!/bin/sh

echo "Checking for missing migrations"
if ! ./manage.py makemigrations --dry-run --check --no-input -v1; then
  echo "Missing migrations detected!"
  exit 1
fi
