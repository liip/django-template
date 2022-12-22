#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import re
import shutil



def uninstall_docker():
    files_to_remove = {
        'entrypoint.sh', 'entrypoint-frontend.sh', 'docker-compose.yml',
        'docker-compose.override.example.yml', 'Dockerfile',
        'Dockerfile-frontend', '.gitlab-ci.yml'
    }

    for file_ in files_to_remove:
        os.remove(file_)


def set_parameter(path, key, value):
    patched_lines = []
    parameter_exists = False

    with open(path) as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('{}:'.format(key)):
            line = '{key}: "{value}"\n'.format(key=key, value=value)
            parameter_exists = True
        patched_lines.append(line)

    if not parameter_exists:
        patched_lines.append('{key}: "{value}"\n'.format(key=key, value=value))

    with open(path, 'w') as f:
        f.write(''.join(patched_lines))


def patch_parameters(path):
    set_parameter(path, 'pip_requirements', 'requirements/dev.txt')
    set_parameter(path, 'pip_requirements_dir', 'requirements')
    set_parameter(path, 'project_name', '{{ cookiecutter.project_slug }}')
    set_parameter(path, 'database_name', '{{ cookiecutter.project_slug }}')
    set_parameter(path, 'hostname', "{{ cookiecutter.project_slug.replace('_', '-') }}.lo")
    set_parameter(path, 'python_version', '3')


def patch_playbook(path):
    patched_lines = []
    roles_to_enable = set(['django', 'postgresql', 'webpack', 'gitlabci'])

    with open(path) as f:
        lines = f.readlines()

    for line in lines:
        role_match = re.search(r'role: (\w+)', line)

        if role_match and role_match.group(1) in roles_to_enable:
            line = line.replace('# -', '-')

        patched_lines.append(line)
    patched_lines.append(
        """
  tasks:
  - name: Make sure rsync is installed
    apt:
      state: present
      pkg: rsync
    become: yes
"""
    )

    with open(path, 'w') as f:
        f.write(''.join(patched_lines))


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
