import json

from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import BaseRegistry
from govstack_api.graphql_api_client import GrapheneClient
from insuree.schema import Query, Mutation


def get_insurees_query(variable_values: str = "", fetched_fields: str = "") -> str:
    return f'''
            query GetInsurees {{
                insurees({variable_values}) {{
                    edges{{
                        node{{
                            {fetched_fields}
                        }}
                    }}
                }}
            }}
            '''


class InsureeRegistry(BaseRegistry):

    def __init__(self, request):
        self.client = GrapheneClient(request, Query, Mutation)
        self.fields_mapping = {
            'ID': 'uuid',
            'FirstName': 'otherNames',
            'LastName': 'lastName',
        }
        self.special_fields = ['BirthCertificateID', 'PersonalData']

    def get_record(self, mapped_data):

        # workaround because for now we lack on filtering json_ext
        fetched_fields = ', '.join(mapped_data.keys())
        mapped_data.pop('jsonExt', None)

        variable_values = ', '.join(f'{field}: "{value}"' for field, value in mapped_data.items())
        query = get_insurees_query(variable_values, fetched_fields)
        result = self.client.execute_query(query)
        first_record = self.extract_records(result, only_first=True)
        return first_record

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

    def extract_records(self, result, only_first=True):
        edges = result.get('data', {}).get('insurees', {}).get('edges', [])
        records = [edge.get('node', {}) for edge in edges]

        if records:
            return records[0] if only_first else records
        else:
            return None



