import json

from django.apps import apps
from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import BaseRegistry, RegistryType
from govstack_api.graphql_api_client import GrapheneClient
from insuree.schema import Query, Mutation

config = apps.get_app_config('govstack_api')


class InsureeRegistry(BaseRegistry, RegistryType):

    def __init__(self, registry_config, request):
        super().__init__(registry_config, request)
        self.client = GrapheneClient(request, Query, Mutation)

    def get_record_field(self, mapped_data, field=None, extension=None):
        insuree_data = self.get_record(mapped_data, field)
        insuree_data = self.change_result_extension(insuree_data, extension)
        return insuree_data

    def retrieve_filtered_records(self, mapped_data):
        return self.get_record(mapped_data, only_first=False)

    def update_registry_record(self, mapped_data_query, mapped_data_write=None):
        return self.manage_registry_record(self.mutations['update'], mapped_data_query, mapped_data_write)

    def create_registry_record(self, mapped_data):
        self.manage_registry_record(self.mutations['create'], mapped_data)
        return self.get_record(mapped_data)

    def update_multiple_records(self, mapped_data=None):
        insuree_uuids = self.extract_uuids(mapped_data, first=False)
        for insuree_uuid in insuree_uuids:
            # For each UUID, we update the corresponding record with the mapped_data
            self.update_registry_record({**mapped_data, "uuid": insuree_uuid})

    def delete_registry_record(self, mapped_data):
        insuree_uuid = self.extract_uuid(mapped_data)
        if insuree_uuid:
            query = self.get_mutation(
                mutation_name=self.mutations['delete'],
                arguments_with_values={f'uuids:[{insuree_uuid}]'},
            )
            self.client.execute_query(query)
            return 204
        else:
            return 404

    def create_or_update_registry_record(self, mapped_data):
        insuree_uuid = self.get_record_field(self, mapped_data, "uuid", "string")
        if insuree_uuid:
            self.update_registry_record(mapped_data)
        else:
            self.create_registry_record(mapped_data)
        return self.get_record(mapped_data)

    def map_to_graphql(self, validated_data):
        mapped_data = {}
        json_ext = {}

        for http_field, value in validated_data.items():
            if http_field in self.fields_mapping:
                graphql_field = self.fields_mapping[http_field]
                mapped_data[graphql_field] = value
            elif http_field in self.special_fields:
                json_ext[http_field] = value

        if json_ext:
            mapped_data['jsonExt'] = json.dumps(json_ext)

        return mapped_data

    def map_from_graphql(self, graphql_data):
        mapped_data = {}
        json_ext = {}
        # We need to reverse the fields_mapping dictionary for map_from_graphql
        reversed_fields_mapping = {v: k for k, v in self.fields_mapping.items()}

        for graphql_field, value in graphql_data.items():
            if graphql_field in reversed_fields_mapping:
                http_field = reversed_fields_mapping[graphql_field]
                mapped_data[http_field] = value
            elif graphql_field == 'jsonExt':
                if value is not None:
                    try:
                        value = json.loads(value)  # First decoding
                        json_ext = json.loads(value)  # Second decoding
                    except json.JSONDecodeError as e:
                        print(f"Cannot decode value: {value}. Error: {e}")
                        json_ext = {}
                else:
                    json_ext = {}
        for special_field in self.special_fields:
            if special_field in json_ext:
                mapped_data[special_field] = json_ext[special_field]

        return mapped_data

    def extract_uuid(self, mapped_data_query):
        insuree_uuid_dict = self.get_record_field(mapped_data=mapped_data_query, field="uuid", extension="json")
        if insuree_uuid_dict != 'null':
            return insuree_uuid_dict.get('uuid')
        else:
            return None

    def get_required_data_for_mutation(self, mapped_data: dict) -> dict:
        """
        This function adapts the input data to the specific schema of the registry.
        """
        adapted_data = self.default_values.copy()
        adapted_data.update(mapped_data)
        if 'chfId' not in adapted_data and 'id' in mapped_data:
            adapted_data['chfId'] = f'chfId: "{mapped_data["id"]}"'
        for key in mapped_data.keys():
            if key in adapted_data:
                del adapted_data[key]
        return adapted_data
