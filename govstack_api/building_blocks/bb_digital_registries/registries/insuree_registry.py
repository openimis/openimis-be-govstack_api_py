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

    def get_record(self, mapped_data):

        variable_values = ', '.join(f'{field}: "{value}"' for field, value in mapped_data.items())
        fetched_fields = ', '.join(mapped_data.keys())
        query = get_insurees_query(variable_values, fetched_fields)
        # execute query using client
        result = self.client.execute_query(query)
        print(result)
        print(query)

    def map_to_graphql(self, validated_data):
        mapped_data = {}

        fields_mapping = {
            'ID': 'uuid',
            'FirstName': 'otherNames',
            'LastName': 'lastName',
            # 'BirthCertificateID': 'jsonExt',
        }

        for http_field, value in validated_data.items():
            if http_field in fields_mapping:
                graphql_field = fields_mapping[http_field]
                mapped_data[graphql_field] = value

        return mapped_data

    def map_from_graphql(self):
        print("map_from_graphql")


