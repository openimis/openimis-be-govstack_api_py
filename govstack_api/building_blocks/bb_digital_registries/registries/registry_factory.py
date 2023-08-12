from typing import Type

from govstack_api.building_blocks.bb_digital_registries.models import Registry
from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import RegistryType

# Note: globals().get(registry_class_name) expects to have registries imported in here.
# noinspection PyUnresolvedReferences
from govstack_api.building_blocks.bb_digital_registries.registries.insuree_registry import InsureeRegistry


class RegistryFactory:
    @staticmethod
    def get_registry(registry_name, version_number, user):
        registry = Registry.objects.get(registry_name=registry_name, version=version_number)
        if registry is None:
            raise ValueError(f"No registry found for name {registry_name} and version {version_number}")
        registry_class_name = registry.class_name

        registry_class: Type[RegistryType] = globals().get(registry_class_name)

        if registry_class is None:
            raise ValueError(f"No registry class found for {registry_class_name}")

        return registry_class(
            {
                "class": registry.class_name,
                "model": registry.model,
                "fields_mapping": registry.fields_mapping,
                "special_fields": registry.special_fields,
                "default_values": registry.default_values,
                "mutations": registry.mutations,
                "queries": registry.queries,
                "registry_name": registry_name,
                "version_number": version_number,
                "user": user
            })
