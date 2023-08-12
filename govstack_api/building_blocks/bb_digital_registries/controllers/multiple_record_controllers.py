from govstack_api.apps import TestHarnessApiConfig
from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def update_multiple_records_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    mapped_data_query = registry.gql_mapper.map_to_graphql(validated_data['query'])
    mapped_data_write = registry.gql_mapper.map_to_graphql(validated_data['write'])
    return registry.update_multiple_records(mapped_data_query, mapped_data_write)


def get_list_of_records_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    data = {validated_data.get('filter'): validated_data.get('search')} if validated_data.get('filter') else {}
    mapped_data = registry.gql_mapper.map_to_graphql(data)
    registry_records = registry.retrieve_filtered_records(
        mapped_data,
        validated_data.get('page', 0),
        validated_data.get('page_size', TestHarnessApiConfig.default_page_size),
        validated_data.get('ordering')
    )
    if registry_records:
        return 200, registry_records
    else:
        return 204, []


class ListViewControler:

    def __init__(self):
        ...
