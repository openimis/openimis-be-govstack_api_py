import os
from django.apps import AppConfig


class TestHarnessApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'govstack_api'

    IM_CLIENT = os.getenv('IM_CLIENT', None)
