import urllib

from govstack_api.apps import TestHarnessApiConfig
from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def update_multiple_records_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    result = registry.update_multiple_records(validated_data['query'], validated_data['write'])
    if result:
        return 200, result
    else:
        return 400, {}


class ListViewController:

    def __init__(self, request, registryname, versionnumber):
        self.registry = RegistryFactory.get_registry(registryname, versionnumber, request.user)
        self.request = request

    def get_records(self, validated_data):
        data = {validated_data.get('filter'): validated_data.get('search')} if validated_data.get('filter') else {}
        result = self.registry.retrieve_filtered_records(
            data,
            validated_data.get('page', 0),
            validated_data.get('page_size', TestHarnessApiConfig.default_page_size),
            validated_data.get('ordering')
        )

        return 200, self._build_response(result, validated_data.copy())

    def _build_response(self, result, input_data):
        output = {
            "count": result['count'],
            "results": result['entries'],
        }

        page = input_data.get('page', 0)
        # Combining the path from the parsed URL to get the desired part
        # TODO: Check if this should be full url projection or just relevant URI path
        base_uri = F"/data/{input_data.pop('registryname')}/{input_data.pop('versionnumber')}"
        if result['has_next_page']:
            input_data['page'] = page+1
            output["next"] = F"{base_uri}/?{urllib.parse.urlencode(input_data)}"

        if page > 0:
            input_data['page'] = page - 1
            output["previous"] = F"{base_uri}/?{urllib.parse.urlencode(input_data)}"

        return output
