from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def update_multiple_records_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data_query = registry.map_to_graphql(validated_data['query'])
    mapped_data_write = registry.map_to_graphql(validated_data['write'])
    return registry.update_multiple_records(mapped_data_query, mapped_data_write)


def get_list_of_records_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql({validated_data['filter']:validated_data['search']})
    registry_records = registry.retrieve_filtered_records(mapped_data, validated_data['page'], validated_data['page_size'])
    if registry_records:
        return 200, registry_records
    else:
        return 204, []
