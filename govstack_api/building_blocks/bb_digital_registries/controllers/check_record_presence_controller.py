from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def check_record_presence_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry_class(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    registry_record = registry.get_record(mapped_data)
    if registry_record:
        registry_record = registry.map_from_graphql(registry_record)
        return 200, True
    else:
        return 404, False
