from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def get_single_record_controller(request, validated_data, registryname, versionnumber):
    # do we want to use a specific serializer?
    factory = RegistryFactory()
    registry = factory.get_registry_class(registryname, versionnumber)
    mapped_data = registry.map_to_graphql(validated_data)
    registry.get_record(mapped_data)
    registry.map_from_graphql()
    # map_from_graphql()
    # return data with status code
    return 200
