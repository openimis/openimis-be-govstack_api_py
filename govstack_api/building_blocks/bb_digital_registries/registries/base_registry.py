import base64
import json
import xml.etree.ElementTree as ET
from typing import Protocol
from xml.dom import minidom


class RegistryType(Protocol):

    def map_to_graphql(self) -> None:
        ...

    def map_from_graphql(self) -> None:
        ...

    def get_record(self) -> None:
        ...

    def get_record_field(self) -> None:
        ...

    def retrieve_filtered_records(self, mapped_data, page, page_size) -> None:
        ...

    def update_record(self) -> None:
        ...

    def update_multiple_records(self) -> None:
        ...

    def create_registry_record(self) -> None:
        ...

    def create_or_update_registry_record(self) -> None:
        ...

    def delete_record(self) -> None:
        ...

    def check_if_record_exists(self) -> None:
        ...


class BaseRegistry:
    def __init__(self, config, request):
        self.fields_mapping = config['fields_mapping']
        self.model = config['model']
        self.special_fields = config['special_fields']
        self.default_values = config['default_values']
        self.queries = config['queries']
        self.mutations = config['mutations']

    def get_record(self, mapped_data, fetched_fields=None, only_first=True, after_cursor=None, first=5):
        # workaround because for now we lack on filtering json_ext
        if not fetched_fields:
            fetched_fields = ' '.join(self.fields_mapping.values())
        elif isinstance(fetched_fields, list):
            fetched_fields = ', '.join(fetched_fields)
        mapped_data.pop('jsonExt', None)
        arguments_with_values = self.create_arguments_with_values(mapped_data)

        if first:
            arguments_with_values += f" first:{first}"
        if after_cursor:
            arguments_with_values = f"after: {after_cursor}"
        query = self.get_single_model_query(self.queries["get"], arguments_with_values, fetched_fields)
        result = self.client.execute_query(query)
        registry_data = self.extract_records(result, self.queries['get'], only_first)
        return registry_data

    def manage_registry_record(self, mutation_name, mapped_data_query, mapped_data_write=None):
        data_to_write = mapped_data_write if mapped_data_write else mapped_data_query

        default_data_values = self.get_required_data_for_mutation(data_to_write)
        arguments_with_values = self.create_arguments_with_values(data_to_write)
        query = self.get_mutation(
            mutation_name=mutation_name,
            arguments_with_values=arguments_with_values,
            default_values=default_data_values
        )
        self.client.execute_query(query)
        return 200

    def get_mutation(self, mutation_name: str, arguments_with_values: str, default_values: dict = {}) -> str:
        if default_values:
            default_values_str = " ".join(default_values.values())
        else:
            default_values_str = ""
        query = f'''
                mutation {{
                    {mutation_name}(
                        input: {{
                            clientMutationId: "552f8e55-ed5a-4e1e-a159-ea8f8cec0560"
                            clientMutationLabel: "Update insuree"
                            {arguments_with_values}
                            {default_values_str}
                        }}
                    ) {{
                        clientMutationId
                        internalId
                    }}
                }}
                '''
        return query

    def get_single_model_query(self, query_name: str, arguments_with_variables: str = "", fetched_fields: str = "") -> str:
        return f'''
                query {{
                    {query_name}({arguments_with_variables}) {{
                    totalCount
                    pageInfo {{ hasNextPage, endCursor }}
                        edges{{
                            cursor
                            node{{
                                {fetched_fields}
                            }}
                        }}
                    }}
                }}
                '''

    def encode_id(self, mapped_data, model_name):
        if 'id' in mapped_data:
            id_value = mapped_data['id']
            mapped_data['id'] = base64.b64encode(f"{id_value}".encode()).decode()
        return mapped_data

    def decode_id(self, encoded_id):
        decoded_string = base64.b64decode(encoded_id).decode()
        model_name, id_value = decoded_string.split(":")
        return id_value

    def extract_records(self, result, query_get, only_first=True):
        edges = result.get('data', {}).get(f'{query_get}', {}).get('edges', [])
        records = [edge.get('node', {}) for edge in edges]
        for record in records:
            if 'id' in record:
                record['id'] = self.decode_id(record['id'])
        if records:
            return records[0] if only_first else records
        else:
            return None

    def dict_to_xml(self, data_dict):
        xml_elements = ET.Element('root')
        for key, value in data_dict.items():
            child = ET.SubElement(xml_elements, key)
            child.text = str(value)
        return minidom.parseString(ET.tostring(xml_elements)).toprettyxml()

    def change_result_extension(self, data, extension):
        if extension == 'json':
            return data
        elif extension == 'string':
            return str(data)
        elif extension == 'xml':
            return self.dict_to_xml(data)
        else:
            raise ValueError(f"Unknown extension type: {extension}")

    def create_arguments_with_values(self, mapped_data: dict) -> str:
        arguments = []
        for field, value in mapped_data.items():
            if field == 'jsonExt' and isinstance(value, str):
                formatted_value = value.replace('"', '\\"')
                arguments.append(f'{field}: "{formatted_value}"')
            elif field == 'id':
                # Due to the fact that the input can be presented either as a plain integer or as an encoded string,
                # it is necessary to implement dual handling mechanisms to accommodate these variations.
                if value.isdigit():
                    arguments.append(f'{field}: {int(value)}')
                else:
                    arguments.append(f'{field}: "{value}"')
            else:
                arguments.append(f'{field}: "{value}"')
        return ', '.join(arguments)
