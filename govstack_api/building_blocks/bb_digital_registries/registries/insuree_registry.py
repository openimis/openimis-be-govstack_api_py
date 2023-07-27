import base64
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from django.apps import apps
from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import BaseRegistry
from govstack_api.graphql_api_client import GrapheneClient
from insuree.schema import Query, Mutation


config = apps.get_app_config('govstack_api')


def get_insurees_query(arguments_with_variables: str = "", fetched_fields: str = "") -> str:
    return f'''
            query GetInsurees {{
                insurees({arguments_with_variables}) {{
                    edges{{
                        node{{
                            {fetched_fields}
                        }}
                    }}
                }}
            }}
            '''


def get_update_registry_query(
        variables_values: str = "",
        family_id="familyId: 1",
        gender_id='genderId: "U"',
        dob=config.date_of_birth,
        head='head: false',
        card_issued='cardIssued: false'
) -> str:
    query = f'''
                mutation {{
                  updateInsuree(
                    input: {{
                      clientMutationId: "552f8e55-ed5a-4e1e-a159-ea8f8cec0560"
                      clientMutationLabel: "Update insuree"
                      {variables_values}
                      dob: "{dob}"
                      chfId: "180000002"
                      otherNames: "Tatra"
                      {family_id}
                      {gender_id}
                      {head}
                      {card_issued}
                    }}
                  ) {{
                    clientMutationId
                    internalId
                  }}
                }}
                '''
    return query


#TODO make it that it will get required fields with some data and then compare if the data is present in mapped that, if no then use. If else the use those fields that are not present inside mapped data
def get_create_registry_query(
        arguments_with_values: str = "",
        family_id="familyId: 1",
        gender_id='genderId: "U"',
        dob=config.date_of_birth,
        head='head: false',
        card_issued='cardIssued: false'
) -> str:
    return f'''
        mutation {{
          createInsuree(
            input: {{
              clientMutationId: "9d738f06-7855-455a-840f-99aa85d2308e"
              clientMutationLabel: "Create insuree"
              chfID: "{arguments_with_values['id']}"
              {arguments_with_values}
              {family_id}
              {gender_id}
              {dob}
              {head}
              {card_issued}
            }}
          ) {{
            clientMutationId
            internalId
          }}
        }}
        '''


class InsureeRegistry(BaseRegistry):

    def __init__(self, request):
        self.client = GrapheneClient(request, Query, Mutation)
        self.fields_mapping = {
            'ID': 'id',
            'FirstName': 'otherNames',
            'LastName': 'lastName',
            'uuid': 'uuid'
        }
        self.special_fields = ['BirthCertificateID', 'PersonalData']

    def get_record(self, mapped_data, fetched_fields=None, only_first=True):
        # workaround because for now we lack on filtering json_ext
        if not fetched_fields:
            fetched_fields = self.create_fetched_fields(mapped_data)
        mapped_data.pop('jsonExt', None)

        mapped_data = self.encode_id(mapped_data)
        arguments_with_values = ', '.join(f'{field}: "{value}"' for field, value in mapped_data.items())
        query = get_insurees_query(arguments_with_values, fetched_fields)
        result = self.client.execute_query(query)
        registry_data = self.extract_records(result, only_first)
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

    def update_registry_record(self, mapped_data_query, mapped_data_write):
        insuree_uuid = self.extract_uuid(mapped_data_query)
        if insuree_uuid:
            mapped_data_write["uuid"] = insuree_uuid
            arguments_with_values = self.create_arguments_with_values(mapped_data_write)
            query = get_update_registry_query(arguments_with_values)
            self.client.execute_query(query)
            return 200
        else:
            return 404

    def create_registry_record(self, mapped_data):
        insuree_uuid = self.extract_uuid(mapped_data)
        if insuree_uuid:
            mapped_data["uuid"] = insuree_uuid
            arguments_with_values = self.create_arguments_with_values(mapped_data)
            query = get_create_registry_query(arguments_with_values)
            self.client.execute_query(query)
            return 200
        else:
            return 404

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

    def extract_records(self, result, only_first=True):
        edges = result.get('data', {}).get('insurees', {}).get('edges', [])
        records = [edge.get('node', {}) for edge in edges]

        if records:
            return records[0] if only_first else records
        else:
            return None

    def extract_uuid(self, mapped_data_query):
        insuree_uuid_json = self.get_record_field(mapped_data=mapped_data_query, field="uuid", extension="json")
        if insuree_uuid_json != 'null':
            insuree_uuid_dict = json.loads(insuree_uuid_json)
            return insuree_uuid_dict.get('uuid')
        else:
            return None

    def dict_to_xml(data_dict):
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

    def encode_id(self, mapped_data):
        if 'id' in mapped_data:
            id_value = mapped_data['id']
            mapped_data['id'] = base64.b64encode(f"Insuree:{id_value}".encode()).decode()
        return mapped_data

    def create_arguments_with_values(self, mapped_data) -> str:
        arguments = []
        for field, value in mapped_data.items():
            if field == 'jsonExt' and isinstance(value, str):
                formatted_value = value.replace('"', '\\"')
                arguments.append(f'{field}: "{formatted_value}"')
            else:
                arguments.append(f'{field}: "{value}"')
        return ', '.join(arguments)

    def create_fetched_fields(self, mapped_data) -> str:
        return ', '.join(mapped_data.keys())
