#!/usr/bin/env bash
pushd .
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/../
make translations
grep fuzzy -r locale/

if [ $? -eq 0 ]; then
    echo "Fuzzy translation strings found"
    exit 1
fi

popd
