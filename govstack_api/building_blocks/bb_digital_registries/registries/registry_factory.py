from govstack_api.building_blocks.bb_digital_registries.registries.insuree_registry import InsureeRegistry


class RegistryFactory:
    def __init__(self):
        self.registry_classes = {
            ("registryname", "111"): InsureeRegistry,
            # ("registryname2", "version2"): ProductRegistry,
            # Dodaj więcej tutaj...
        }

    def get_registry_class(self, registryname, versionnumber):
        registry_class = self.registry_classes.get((registryname, versionnumber))
        if registry_class is None:
            raise ValueError(f"Unsupported registry: {registryname} version: {versionnumber}")
        return registry_class()
