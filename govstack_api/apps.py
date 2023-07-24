from django.apps import AppConfig


class TestHarnessApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'govstack_api'

    IM_CLIENT = 'eGovStack/GOV/90000009/digitalregistries'