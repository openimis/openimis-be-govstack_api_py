import base64
import json
import uuid
import xml.etree.ElementTree as ET
from functools import cached_property
from typing import Protocol, Dict, Any, Type
from xml.dom import minidom

import graphene

from govstack_api.graphql_api_client import GrapheneClient


class RegistryType(Protocol):

    def __init__(self, config):
        ...

    def map_to_graphql(self, validated_data) -> None:
        ...

    def map_from_graphql(self, graphql_data) -> None:
        ...

    def get_record(self) -> None:
        ...

    def get_record_field(self, mapped_data, field=None, extension=None) -> None:
        ...

    def retrieve_filtered_records(self, mapped_data, page, page_size) -> None:
        ...

    def update_record(self) -> None:
        ...

    def update_multiple_records(self, mapped_data_query: dict = {}, mapped_data_write: dict = {}) -> int:
        ...

    def create_registry_record(self, mapped_data) -> None:
        ...

    def create_or_update_registry_record(self) -> None:
        ...

    def delete_record(self) -> None:
        ...

    def check_if_record_exists(self) -> None:
        ...


class RegistryDetails:
    fields_mapping: Dict[str, Any]
    model: str
    special_fields: Dict[str, Any]
    default_values: Dict[str, Any]
    queries: Dict[str, Any]
    mutations: Dict[str, Any]


class DataConverterUtils:
    """Handles the conversion of data formats."""

    @staticmethod
    def extract_records(result, query_get, only_first=True):
        edges = result.get('data', {}).get(f'{query_get}', {}).get('edges', [])
        records = [edge.get('node', {}) for edge in edges]
        for record in records:
            if 'id' in record:
                record['id'] = DataConverterUtils.decode_id(record['id'])
        if records:
            return records[0] if only_first else records
        else:
            return None

    # ToDO: Check if it's used
    @staticmethod
    def encode_id(mapped_data, model_name):
        if 'id' in mapped_data:
            id_value = mapped_data['id']
            mapped_data['id'] = base64.b64encode(f"{id_value}".encode()).decode()
        return mapped_data

    @staticmethod
    def decode_id(encoded_id):
        decoded_string = base64.b64decode(encoded_id).decode()
        _, id_value = decoded_string.split(":")
        return id_value

    @staticmethod
    def dict_to_xml(data_dict):
        xml_elements = ET.Element('root')
        for key, value in data_dict.items():
            child = ET.SubElement(xml_elements, key)
            child.text = str(value)
            return minidom.parseString(ET.tostring(xml_elements)).toprettyxml()

    @staticmethod
    def change_result_extension(data, extension):
        if extension == 'json':
            return data
        elif extension == 'string':
            return str(data)
        elif extension == 'xml':
            return DataConverterUtils.dict_to_xml(data)
        else:
            raise ValueError(f"Unknown extension type: {extension}")


class DataMapper:
    """Handles mapping data between GraphQL and HTTP."""

    def __init__(self, fields_mapping, special_fields):
        self.fields_mapping = fields_mapping
        self.special_fields = special_fields

    def map_to_graphql(self, validated_data):
        mapped_data = {}
        json_ext = {}
        for http_field, value in validated_data.items():
            if http_field in self.fields_mapping:
                graphql_field = self.fields_mapping[http_field]
                mapped_data[graphql_field] = value
            elif http_field in self.special_fields:
                json_ext[http_field] = value
            else:
                raise ValueError(f"Unsupported field: {http_field}")

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


class GQLPayloadTemplate:
    def get_mutation(self, mutation_name: str, arguments_with_values: str, default_values: dict = {}) -> str:
        if default_values:
            default_values_str = " ".join(default_values.values())
        else:
            default_values_str = ""
        query = f'''
                mutation {{
                    {mutation_name}(
                        input: {{
                            clientMutationId: "{uuid.uuid4()}"
                            clientMutationLabel: "GovStack Digital Registry BB Action"
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


class GQLPayloadBuilder:
    GQL_PAYLOAD_TEMPLATE = GQLPayloadTemplate()

    def __init__(self, fields_mapping, special_fields, default_values):
        self.fields_mapping = fields_mapping
        self.special_fields = special_fields
        self.default_values = default_values
        self.gql_mapper = DataMapper(self.fields_mapping, self.special_fields)

    def build_list_query(self, query_name, data, ordering, page, page_size):
        mapped_data = self.gql_mapper.map_to_graphql(data)
        fetched_fields = ' '.join(self.fields_mapping.values())
        mapped_data.pop('jsonExt', None)
        arguments_with_values = self.create_arguments_with_values(mapped_data)
        if page_size:
            arguments_with_values += f' first:{page_size}'
        if page:
            arguments_with_values += f' offset: "{page * page_size}"'
        if ordering and mapped_data:
            sort_field = list(mapped_data.keys())[0]
            order_arg = f'"{sort_field}"'
            if ordering == 'descending':
                order_arg = f'"-{sort_field}"'
            arguments_with_values += f' orderBy: [{order_arg}]'
        query = self.GQL_PAYLOAD_TEMPLATE.get_single_model_query(
            query_name, arguments_with_values, fetched_fields)
        return query

    @staticmethod
    def create_arguments_with_values(mapped_data: dict) -> str:
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

    def build_mutation(self, data_to_write, mutation_name):
        mapped_data = self.gql_mapper.map_to_graphql(data_to_write)
        default_data_values = self.fill_payload_with_defaults(mapped_data)
        arguments_with_values = self.create_arguments_with_values(mapped_data)
        query = self.GQL_PAYLOAD_TEMPLATE.get_mutation(
            mutation_name=mutation_name,
            arguments_with_values=arguments_with_values,
            default_values=default_data_values
        )
        return query

    def fill_payload_with_defaults(self, mapped_data: dict) -> dict:
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

    def build_record_query(self, query_name, data, after_cursor, fetched_fields, first):
        mapped_data = self.gql_mapper.map_to_graphql(data)
        if not fetched_fields:
            default_fetched_fields = [v for k, v in self.fields_mapping.items() if k != 'uuid']
            default_fetched_fields.append(" jsonExt")
            fetched_fields = ' '.join(default_fetched_fields)
        elif isinstance(fetched_fields, list):
            fetched_fields = ', '.join(fetched_fields)
        mapped_data.pop('jsonExt', None)
        arguments_with_values = self.create_arguments_with_values(mapped_data)
        if first:
            arguments_with_values += f" first:{first}"
        if after_cursor:
            arguments_with_values = f"after: {after_cursor}"
        query = self.GQL_PAYLOAD_TEMPLATE.get_single_model_query(query_name, arguments_with_values,
                                                                 fetched_fields)
        return query


class RegistryGQLManager:
    def __init__(self, user, gql_query, gql_mutation, payload_builder: GQLPayloadBuilder):
        self.client = GrapheneClient(user, gql_query, gql_mutation)
        self.payload_builder = payload_builder

    def mutate_registry_record(self, mutation_name, data):
        query = self.payload_builder.build_mutation(data, mutation_name)
        mutation_result = self.client.execute_query(query)
        return 200

    def retrieve_filtered_records(
            self, data: dict = None, query_name: str = None,
            page: int = None,
            page_size: int = None, ordering=None
    ):
        response_data = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        query = self.payload_builder.build_list_query(query_name, data, ordering, page, page_size)
        result = self.client.execute_query(query)
        extracted_records = DataConverterUtils.extract_records(result=result, query_get=query_name, only_first=False)
        response_data["results"].extend(extracted_records)
        response_data["count"] = result['data'][query_name]['totalCount']
        return {
            'entries': extracted_records,
            'count': result['data'][query_name]['totalCount'],
            'has_next_page': result['data'][query_name]['pageInfo']['hasNextPage']
        }

    def get_record(self, data, query_name, fetched_fields=None, only_first=True, after_cursor=None, first=5):
        # workaround because for now we lack on filtering json_ext
        query = self.payload_builder.build_record_query(
            query_name, data, after_cursor, fetched_fields, first)
        result = self.client.execute_query(query)
        registry_data = DataConverterUtils.extract_records(result, query_name, only_first)
        return registry_data


class BaseRegistryABC:
    @property
    def GQLQuery(self) -> graphene.ObjectType:
        raise NotImplementedError()

    @property
    def GQLMutation(self) -> graphene.ObjectType:
        raise NotImplementedError()

    @property
    def data_converter_type(self) -> Type[DataConverterUtils]:
        return DataConverterUtils

    @property
    def gql_mapper_type(self) -> Type[DataMapper]:
        return DataMapper

    GQL_PAYLOAD_TEMPLATE = GQLPayloadTemplate()

    def __init__(self, config):
        payload_builder = GQLPayloadBuilder(
            fields_mapping=config['fields_mapping'],
            special_fields=config['special_fields'],
            default_values=config['default_values'],
        )
        self.registry_gql_manager = RegistryGQLManager(
            user=config['user'],
            gql_query=self.GQLQuery,
            gql_mutation=self.GQLMutation,
            payload_builder=payload_builder
        )
        self.model = config['model']
        self.queries = config['queries']
        self.mutations = config['mutations']

    def retrieve_filtered_records(
            self, data: dict = None, page: int = None,
            page_size: int = None, ordering=None
    ):
        return self.registry_gql_manager.retrieve_filtered_records(
            data, self.queries['get'], page, page_size, ordering
        )

    def update_multiple_records(self, data: dict = None, updated_data: dict = None) -> int:
        records = self.registry_gql_manager.get_record(
            data=data,
            query_name=self.queries['get'],
            fetched_fields=['uuid'],
            only_first=False
        )
        for record in records:
            updated_data = {**record, **updated_data}
            self.update_registry_record(updated_data)
        return 200

    def create_registry_record(self, mapped_data):
        self.registry_gql_manager.mutate_registry_record(self.mutations['create'], mapped_data)
        return self.registry_gql_manager.get_record(mapped_data, self.queries['get'])

    def update_registry_record(self, mapped_data_query: dict = None, mapped_data_write: dict = None):
        if mapped_data_write and "uuid" not in mapped_data_write:
            record_uuid = self.extract_uuid(mapped_data_query)
            if record_uuid:
                mapped_data_write["uuid"] = record_uuid
        return self.mutate_registry_record(self.mutations['update'], mapped_data_query, mapped_data_write)

    def delete_registry_record(self, mapped_data):
        insuree_uuid = self.extract_uuid(mapped_data)
        if insuree_uuid:
            query = self.GQL_PAYLOAD_TEMPLATE.get_mutation(
                mutation_name=self.mutations['delete'],
                arguments_with_values=f'''uuids: {json.dumps([insuree_uuid])}''',
            )
            self.client.execute_query(query)
            return 204
        else:
            return 404

    def create_or_update_registry_record(self, mapped_data_query: dict = None, mapped_data_write: dict = None):
        insuree_uuid = self.get_record_field(mapped_data_query, field="uuid", extension="string")
        if insuree_uuid != "None":
            self.update_registry_record(mapped_data_query, mapped_data_write)
        else:
            self.create_registry_record(mapped_data_write)
        return self.get_record(mapped_data_write)

    def get_record_field(self, mapped_data=None, field=None, extension=None, only_first=True):
        insuree_data = self.get_record(mapped_data, field, only_first=only_first)
        insuree_data = self.data_converter.change_result_extension(insuree_data, extension)
        return insuree_data

    def extract_uuid(self, mapped_data_query, only_first=True):
        returned_uuid = self.get_record_field(
            mapped_data=mapped_data_query, field="uuid", extension="json", only_first=only_first
        )
        if returned_uuid and returned_uuid != 'null':
            return returned_uuid.get('uuid')
        else:
            return None


class BaseRegistry(BaseRegistryABC):
    ...