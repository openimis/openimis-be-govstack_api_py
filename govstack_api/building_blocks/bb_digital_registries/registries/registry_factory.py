from govstack_api.building_blocks.bb_digital_registries.registries.insuree_registry import InsureeRegistry
from django.apps import apps


class RegistryFactory:
    def __init__(self):
        config = apps.get_app_config('govstack_api')
        self.registry_config_data = config.registry_config_data

    def get_registry(self, registry_name, version_number, request):
        registry_config = self.registry_config_data.get(registry_name, {}).get(str(version_number))
        if registry_config is not None:
            registry_class_name = registry_config['class']
            registry_class = globals().get(registry_class_name)
            if registry_class is None:
                raise ValueError(f"No registry class found for {registry_class_name}")
            return registry_class(registry_config, request)

        raise ValueError(f"No registry found for name {registry_name} and version {version_number}")