import os
from django.conf import settings

from django.apps import AppConfig


MODULE_NAME = "govstack_api"
DEFAULT_CFG = {
    'default_page_size': 50,
}


class TestHarnessApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = MODULE_NAME

    IM_CLIENT = os.getenv('IM_CLIENT', None)

    default_page_size = 50

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_perms(cfg)

        if 'govstack_api.middleware.InformationMediatorMiddleware' not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.append('govstack_api.middleware.InformationMediatorMiddleware')

        if 'govstack_api.middleware.ContentTypeMiddleware' not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.append('govstack_api.middleware.ContentTypeMiddleware')

    def _configure_perms(self, cfg):
        TestHarnessApiConfig.page_size = cfg['default_page_size']
