import json
import os
from django.apps import AppConfig


class TestHarnessApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'govstack_api'

    IM_CLIENT = os.getenv('IM_CLIENT', None)

    date_of_birth = '1920-04-02'

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'registry_config.json')
    with open(config_path, 'r') as json_file:
        registry_config_data = json.load(json_file)
