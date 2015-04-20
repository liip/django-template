#!/usr/bin/env python
import os
import sys

from {{ project_name }} import get_project_root_path, import_env_vars


if __name__ == "__main__":
    if 'test' in sys.argv:
        env_dir = os.path.join('envdir', 'tests')
    else:
        env_dir = os.path.join('envdir', 'local')

    import_env_vars(os.path.join(get_project_root_path(), env_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
