#!/bin/sh

echo "Checking for missing migrations"
./manage.py makemigrations --dry-run --check --no-input -v1
if [ $? != 0 ]; then
    echo "Missing migrations detected!"
    exit 1
fi
exit 0
