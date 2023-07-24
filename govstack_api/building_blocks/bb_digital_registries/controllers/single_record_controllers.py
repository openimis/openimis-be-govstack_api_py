from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def get_single_record_controller(request, validated_data, registryname, versionnumber):
    # do we want to use a specific serializer?
    factory = RegistryFactory()
    registry = factory.get_registry_class(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    registry_record = registry.get_record(mapped_data)
    if registry_record:
        registry_record = registry.map_from_graphql(registry_record)
        return 200, registry_record
    else:
        return 204, {}
