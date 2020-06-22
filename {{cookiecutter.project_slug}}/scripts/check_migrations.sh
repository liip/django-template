#!/bin/sh

echo "Checking for missing migrations"
export DATABASE_URL=sqlite://memory  # remove requirement for existing database
./manage.py makemigrations --dry-run --check --no-input -v1 || { echo "Missing migrations detected!"; exit 1; }
exit 0
