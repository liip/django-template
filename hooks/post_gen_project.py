#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import shutil


def uninstall_docker():
    files_to_remove = {
        'entrypoint.sh', 'entrypoint-frontend.sh', 'docker-compose.yml',
        'docker-compose.override.example.yml', 'Dockerfile',
        'Dockerfile-frontend', '.gitlab-ci.yml'
    }

    for file_ in files_to_remove:
        os.remove(file_)


def generate_blank_locale_files():
    for lang in '{{ cookiecutter.language_list }}'.split(','):
        os.mkdir('locale/{}'.format(lang))
        os.mkdir('locale/{}/LC_MESSAGES'.format(lang))
        open('locale/{}/LC_MESSAGES/django.po'.format(lang), 'w').close()


if __name__ == '__main__':
    use_docker = '{{ cookiecutter.virtualization_tool }}' == 'docker'

    if not use_docker:
        uninstall_docker()

    if '{{ cookiecutter.override_user_model }}' == 'n':
        shutil.rmtree('{{ cookiecutter.project_slug }}/accounts')

    generate_blank_locale_files()

    print("\n(~˘▾˘)~ Your project `{{ cookiecutter.project_slug }}` is ready, have a nice day! ~(˘▾˘~)")
    if use_docker:
        print("Please follow the instructions in the docker-compose.override.example.yml file to get started.")
