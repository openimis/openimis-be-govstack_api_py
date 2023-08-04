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

    def get_record_field(self, mapped_data, field=None, extension=None, only_first=True):
        insuree_data = self.get_record(mapped_data, field, only_first=only_first)
        insuree_data = self.change_result_extension(insuree_data, extension)
        return insuree_data

    def retrieve_filtered_records(self, mapped_data, page, page_size):
        after_cursor = None
        previous_cursor = None
        response_data = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        for _ in range(page):
            fetched_fields = ' '.join(self.fields_mapping.values())
            mapped_data.pop('jsonExt', None)
            arguments_with_values = self.create_arguments_with_values(mapped_data)
            if page_size:
                arguments_with_values += f' first:{page_size}'
            if after_cursor:
                arguments_with_values += f' after: "{after_cursor}"'
            query = self.get_single_model_query(self.queries["get"], arguments_with_values, fetched_fields)
            result = self.client.execute_query(query)
            if not result['data'][self.queries['get']]['edges']:
                break
            last_record = result['data'][self.queries['get']]['edges'][-1]
            previous_cursor = after_cursor
            after_cursor = last_record['cursor']
        extracted_records = self.extract_records(result=result, query_get=self.queries['get'], only_first=False)
        response_data["results"].extend(extracted_records)
        response_data["count"] = result['data'][self.queries['get']]['totalCount']
        response_data["next"] = after_cursor if result['data'][self.queries['get']]['pageInfo']['hasNextPage'] else None
        response_data["previous"] = previous_cursor

        return response_data

    def update_registry_record(self, mapped_data_query, mapped_data_write={}):
        if "uuid" not in mapped_data_write:
            record_uuid = self.extract_uuid(mapped_data_query)
            if record_uuid:
                mapped_data_write["uuid"] = record_uuid
        return self.manage_registry_record(self.mutations['update'], mapped_data_query, mapped_data_write)

    def create_registry_record(self, mapped_data):
        self.manage_registry_record(self.mutations['create'], mapped_data)
        return self.get_record(mapped_data)

    def update_multiple_records(self, mapped_data_query: dict, mapped_data_write: dict) -> int:
        records = self.get_record(
            mapped_data=mapped_data_query,
            fetched_fields=['lastName', 'otherNames', 'id', 'chfId', 'uuid'],
            only_first=False
        )
        for record in records:
            updated_data = {**record, **mapped_data_write}
            self.update_registry_record(updated_data)
        return 200

    def delete_registry_record(self, mapped_data):
        insuree_uuid = self.extract_uuid(mapped_data)
        if insuree_uuid:
            query = self.get_mutation(
                mutation_name=self.mutations['delete'],
                arguments_with_values=f'''uuids: {json.dumps([insuree_uuid])}''',
            )
            self.client.execute_query(query)
            return 204
        else:
            return 404

    def create_or_update_registry_record(self, mapped_data_query, mapped_data_write):
        insuree_uuid = self.get_record_field(mapped_data_query, field="uuid", extension="string")
        if insuree_uuid != "None":
            self.update_registry_record(mapped_data_query, mapped_data_write)
        else:
            self.create_registry_record(mapped_data_write)
        return self.get_record(mapped_data_write)

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

    def extract_uuid(self, mapped_data_query, only_first=True):
        returned_uuid = self.get_record_field(
            mapped_data=mapped_data_query, field="uuid", extension="json", only_first=only_first
        )
        if returned_uuid and returned_uuid != 'null':
            return returned_uuid.get('uuid')
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
