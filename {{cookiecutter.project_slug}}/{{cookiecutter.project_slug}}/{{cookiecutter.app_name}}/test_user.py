from django.contrib.auth import get_user_model


def test_user_creation(settings, user_factory):
    user_factory()
    assert get_user_model().objects.all().count() == 1
