import json

from django.apps import apps
from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import BaseRegistry, RegistryProtocol
from govstack_api.graphql_api_client import GrapheneClient
from insuree.schema import Query, Mutation

config = apps.get_app_config('govstack_api')


class InsureeRegistry(BaseRegistry, RegistryProtocol):

    def __init__(self, registry_config, request):
        super().__init__(registry_config, request)
        self.client = GrapheneClient(request, Query, Mutation)

    def get_record(self, mapped_data, fetched_fields=None, only_first=True):
        # workaround because for now we lack on filtering json_ext
        if not fetched_fields:
            fetched_fields = self.create_fetched_fields(mapped_data)
        mapped_data.pop('jsonExt', None)
        mapped_data = self.insuree_encode_id(mapped_data)
        arguments_with_values = self.create_arguments_with_values(mapped_data)
        query = self.get_single_model_query(self.queries["get"], arguments_with_values, fetched_fields)
        result = self.client.execute_query(query)
        registry_data = self.extract_insuree_records(result, self.queries['get'], only_first)
        return registry_data

    def read_record(self, mapped_data, only_first=True):
        # it can be function above without common part
        pass

    def get_record_field(self, mapped_data, field=None, extension=None):
        insuree_data = self.get_record(mapped_data, field)
        insuree_data = self.change_result_extension(insuree_data, extension)
        return insuree_data

    def retrieve_filtered_records(self, mapped_data):
        return self.get_record(mapped_data, only_first=False)

    def manage_registry_record(self, mutation_name, mapped_data_query, mapped_data_write=None):
        insuree_uuid = self.extract_uuid(mapped_data_query)
        if insuree_uuid:
            data_to_write = mapped_data_write if mapped_data_write else mapped_data_query
            data_to_write["uuid"] = insuree_uuid
            default_data_values = self.get_required_data_for_mutation(data_to_write)
            arguments_with_values = self.create_arguments_with_values(data_to_write)
            query = self.get_mutation(
                mutation_name=mutation_name,
                arguments_with_values=arguments_with_values,
                default_values=default_data_values
            )
            self.client.execute_query(query)
            return 200
        else:
            return 404

    def update_registry_record(self, mapped_data_query, mapped_data_write):
        return self.manage_registry_record(self.mutations['update'], mapped_data_query, mapped_data_write)

    def create_registry_record(self, mapped_data):
        return self.manage_registry_record(self.mutations['update'], mapped_data)

    def create_or_update_registry_record(self, mapped_data):
        insuree_uuid = self.get_record_field(self, mapped_data, "uuid", "string")
        if insuree_uuid:
            self.update_registry_record(mapped_data)
        else:
            self.create_registry_record(mapped_data)

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
                    json_ext = json.loads(value)
                else:
                    json_ext = {}

        for special_field in ['BirthCertificateID', 'PersonalData']:
            if special_field in json_ext:
                mapped_data[special_field] = json_ext[special_field]

        return mapped_data

    def extract_insuree_records(self, result, query_get, only_first=True):
        return self.extract_records(result, query_get, only_first)

    def extract_uuid(self, mapped_data_query):
        insuree_uuid_json = self.get_record_field(mapped_data=mapped_data_query, field="uuid", extension="json")
        if insuree_uuid_json != 'null':
            insuree_uuid_dict = json.loads(insuree_uuid_json)
            return insuree_uuid_dict.get('uuid')
        else:
            return None

    def insuree_encode_id(self, mapped_data):
        return self.encode_id(mapped_data, "Insuree")

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

    def create_arguments_with_values(self, mapped_data: dict) -> str:
        arguments = []
        for field, value in mapped_data.items():
            if field == 'jsonExt' and isinstance(value, str):
                formatted_value = value.replace('"', '\\"')
                arguments.append(f'{field}: "{formatted_value}"')
            elif field == 'id':
                try:
                    value = int(value)
                    arguments.append(f'{field}: {value}')
                except ValueError:
                    arguments.append(f'{field}: "{value}"')
            else:
                arguments.append(f'{field}: "{value}"')
        return ', '.join(arguments)
