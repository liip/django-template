#!/bin/sh

echo "Checking for missing migrations"
./manage.py makemigrations --dry-run --check --no-input -v1 || (echo "Missing migrations detected!" && exit 1)
exit 0
