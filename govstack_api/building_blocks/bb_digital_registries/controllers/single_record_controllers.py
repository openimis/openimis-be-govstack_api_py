from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def read_single_record_controller(request, validated_data, registryname, versionnumber):
    # do we want to use a specific serializer?
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    registry_record = registry.get_record(mapped_data)
    if registry_record:
        registry_record = registry.map_from_graphql(registry_record)
        return 200, registry_record
    else:
        return 404, {}


def check_record_presence_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    registry_record = registry.get_record(mapped_data)
    if registry_record:
        return 200, True
    else:
        return 404, False


def get_single_record_field_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    registry_record_field = registry.get_record_field(
        mapped_data, validated_data, validated_data['field'], validated_data['ext']
    )
    if registry_record_field:
        return 200, registry_record_field
    else:
        return 404, {}


def update_single_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data_query = registry.map_to_graphql(validated_data['query'])
    mapped_data_write = registry.map_to_graphql(validated_data['write'])
    registry_record_field = registry.update_registry_record(mapped_data_query, mapped_data_write)
    return registry_record_field


def create_single_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data['write'])
    registry_record = registry.create_registry_record(mapped_data)
    if registry_record:
        return 200, registry_record
    else:
        return 404, {}


def create_or_update_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    registry_record = registry.create_or_update_registry_record(mapped_data)
    if registry_record:
        registry_record = registry.map_from_graphql(registry_record)
        return 200, registry_record
    else:
        return 404, {}


def delete_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request)
    mapped_data = registry.map_to_graphql(validated_data)
    return registry.delete_registry_record(mapped_data)

