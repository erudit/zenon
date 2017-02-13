# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model

import logging

logger = logging.getLogger(__name__)


def get_or_create_legacy_user(username, email, hashed_password=None):
    """ Gets or creates a user.

    This function is aimed to be used in an import script.
    """
    user = None
    user_model = get_user_model()
    try:
        user = user_model.objects.get(email=email)
        # If the user exists this means that we are importing a user from multiple databases.
        # So we will deactivate his password in order to force him recreate it.
        user.set_unusable_password()
        user.save()
    except user_model.DoesNotExist:
        try:
            user_model.objects.get(username=username)
            logger.warn("A user with the username {} already exists. Cannot create.")
        except user_model.DoesNotExist:
            user = user_model.objects.create(username=username, email=email)
            user.password = hashed_password
            user.save()
    return user
