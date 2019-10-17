#!/bin/sh

if [ "$INITIAL" = "1" ]; then
    npm install
fi

exec "${@}"
