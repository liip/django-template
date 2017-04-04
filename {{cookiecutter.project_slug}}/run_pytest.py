#!/usr/bin/env python

import pytest
import os
import sys

# we need this wrapper in order to be able to set the environment
# variables from envdir

from {{ cookiecutter.project_slug }} import get_project_root_path, import_env_vars

import_env_vars(os.path.join(get_project_root_path(), 'envdir'))

sys.exit(pytest.main())
