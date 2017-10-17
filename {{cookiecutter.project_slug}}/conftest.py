import pytest
from {{cookiecutter.project_slug}}.{{cookiecutter.app_name}} import factories as {{cookiecutter.app_name}}_factories
from pytest_factoryboy import register


# enable database for all tests
@pytest.fixture(autouse=True)
def enable_db(db):
    pass


register({{cookiecutter.app_name}}_factories.UserFactory)
