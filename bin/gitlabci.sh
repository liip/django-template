#!/bin/sh
set -e

finish() {
    vagrant halt
}

trap finish EXIT INT

git submodule update --init

vagrant up --provider lxc
vagrant provision
vagrant ssh -c "tox -r"
