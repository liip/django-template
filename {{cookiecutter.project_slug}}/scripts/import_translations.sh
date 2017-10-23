#!/usr/bin/env bash
set -e
if [ "$#" -ne 2 ]; then
    echo "Usage: ./scripts/import_translations <locale> <.po file to import>"
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LANGUAGE=$1
FILE_TO_IMPORT=$2

msgcat --use-first $FILE_TO_IMPORT $DIR/../locale/$LANGUAGE/LC_MESSAGES/django.po -o $DIR/../locale/$LANGUAGE/LC_MESSAGES/django.po
