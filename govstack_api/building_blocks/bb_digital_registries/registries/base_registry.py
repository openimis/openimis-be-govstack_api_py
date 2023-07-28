import base64
import json
import xml.etree.ElementTree as ET
from typing import Protocol
from xml.dom import minidom


class RegistryProtocol(Protocol):
    def get_record(self) -> None:
        ...

    def update_record(self) -> None:
        ...

    def delete_record(self) -> None:
        ...

    def check_if_record_exists(self) -> None:
        ...


class BaseRegistry:
    def __init__(self, config, request):
        self.fields_mapping = config['fields_mapping']
        self.special_fields = config['special_fields']
        self.default_values = config['default_values']
        self.queries = config['queries']
        self.mutations = config['mutations']

    def get_mutation(self, mutation_name: str, arguments_with_values: str, default_values: dict) -> str:
        default_values_str = " ".join(default_values.values())
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
                        edges{{
                            node{{
                                {fetched_fields}
                            }}
                        }}
                    }}
                }}
                '''

    def create_fetched_fields(self, mapped_data) -> str:
        return ', '.join(mapped_data.keys())

    def encode_id(self, mapped_data, model_name):
        if 'id' in mapped_data:
            id_value = mapped_data['id']
            mapped_data['id'] = base64.b64encode(f"{model_name}:{id_value}".encode()).decode()
        return mapped_data

    def extract_records(self, result, query_get, only_first=True):
        edges = result.get('data', {}).get(f'{query_get}', {}).get('edges', [])
        records = [edge.get('node', {}) for edge in edges]

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
            return json.dumps(data)
        elif extension == 'string':
            return str(data)
        elif extension == 'xml':
            return self.dict_to_xml(data)
        else:
            raise ValueError(f"Unknown extension type: {extension}")
