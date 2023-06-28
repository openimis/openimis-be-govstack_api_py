from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from django.http import HttpResponse
import json
from graphene import Schema
from insuree.schema import Query, Mutation
from insuree.models import Insuree
# from contribution_plan.tests.gql_tests.query_tests import *
from graphene import Schema

from .swaggers_schema import (
    create_request_body,
    create_response_body,
    get_multiple_records_from_registry_parameters,
    exists_request_body,
    exists_response_body, update_record_schema, read_record_schema
)
from .services import (
    check_if_registry_exists,
    QueryTest, get_client, get_context
)

@swagger_auto_schema(
    method='GET',
    operation_description="Creates a new record in the registry database.",
    manual_parameters=get_multiple_records_from_registry_parameters,
    responses={200: create_response_body},
)
@api_view(['GET'])
def get_multiple_records_from_registry(request, registryname, versionnumber):
    search = request.GET.get('search')
    filter = request.GET.get('filter')
    ordering = request.GET.get('ordering', "-id")
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    query_fieldname = request.GET.get('query.<fieldname>')

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variable_values = "first: 1, "
    variables = {}
    if ordering == "descending":
        ordering = f"-{filter}"
    else:
        ordering = filter

    if query_fieldname:
        fetched_fields = query_fieldname
    else:
        fetched_fields = 'id, lastName, otherNames'

    result = client.execute(f'''
        query GetInsurees {{
            insurees(orderBy: "{ordering}", {filter}:"{search}" ) {{
                edges{{
                    node{{
                        {fetched_fields}
                    }}
                }}
            }}
        }}
        ''', context=context, variables=variables)
    node_list = [edge['node'] for edge in result['data']['insurees']['edges']]
    if len(result['data']['insurees']['edges']) > 0:
        message = "Object found from database"
    else:
        message = "Object not found from database"

    response_data = {
        "count": len(result['data']['insurees']['edges']),
        "next": 1,
        "previous": "string",
        "results": node_list  # Convert queryset or field values to a list
    }

    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(
    method='post',
    operation_description="Create new record",
    request_body=create_request_body,
    responses={200: create_response_body},
)
@api_view(['POST'])
def create_new_record_in_registry(request, registryname, versionnumber):
    query_content = request.data.get('write', {}).get('content')
    if not query_content:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    # Variables to insert into the query.
    if 'ID' in query_content:
        # slice it to match 12 chars limit
        chf_id = query_content['ID'][:12]
    if 'FirstName' in query_content:
        first_name = query_content['FirstName']
    if 'LastName' in query_content:
        last_name = query_content['LastName']
    if 'BirthCertificateID' in query_content:
        birth_certificate_id = query_content['BirthCertificateID']

    variables = {
        'clientMutationLabel': f'Create insuree - {chf_id}',
        'chfId': chf_id,
        'lastName': f'{first_name}',
        'otherNames': f'{last_name}',
        'genderId': 'M',
        'dob': '2000-06-20',
        'head': True,
        'cardIssued': False,
        'jsonExt': '{}',
    }

    query = f'''
    mutation {{
        createInsuree(
            input: {{
                clientMutationLabel: "{variables['clientMutationLabel']}"
                chfId: "{variables['chfId']}"
                lastName: "{variables['lastName']}"
                otherNames: "{variables['otherNames']}"
                genderId: "{variables['genderId']}"
                dob: "{variables['dob']}"
                head: {str(variables['head']).lower()}
                cardIssued: {str(variables['cardIssued']).lower()}
                jsonExt: "{variables['jsonExt']}"
                familyId: 1
            }}
        ) {{
            clientMutationId
            internalId
        }}
    }}
    '''

    client.execute(query, context=context, variables=variables)
    response_data = {
        "content": {
            "ID": chf_id,
            "FirstName": f'{first_name}',
            "LastName": f'{last_name}',
            "BirthCertificate": ""
        }
    }
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response



@swagger_auto_schema(
    method='post',
    operation_description="Searches records based on input parameters and returns boolean answer (true/false).",
    request_body=exists_request_body,
    responses={200: exists_response_body},
)
@api_view(['POST'])
def check_if_record_exists_in_registry(request, registryname, versionnumber):
    query_content = request.data.get('query', {}).get('content')

    if not query_content:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variable_values = "first: 1, "
    variables = {}

    if 'ID' in query_content:
        variable_values += f'chfId: "{query_content["ID"]}",'
    if 'FirstName' in query_content:
        variable_values += f'otherNames: "{query_content["FirstName"]}",'
    if 'LastName' in query_content:
        variable_values += f'lastName: "{query_content["LastName"]}",'
    # if 'BirthCertificateID' in query_content:
    #     variable_values += ": $"
    variable_values = variable_values[:-1]

    result = client.execute(f'''
    query GetInsurees{{
        insurees({variable_values}) {{
            edges{{
                node{{
                    lastName
                }}
            }}
        }}
    }}
    ''', context=context, variables=variables)
    if len(result['data']['insurees']['edges']) > 0:
        message = "Object found from database"
    else:
        message = "Object not found from database"

    response_data = {
        "answer": {
            "status": 200,
            "message": message
        }
    }

    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(**update_record_schema)
@api_view(['PUT'])
def update_single_record_in_registry(request, registryname, versionnumber):
    query_content = request.data.get('query', {}).get('content')
    query_write = request.data.get('write', {}).get('content')

    if not query_content and not query_write:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    content_values = {}
    write_values = {}
    # Variables to insert into the query.

    content_values['chfId'] = query_content.get('ID', "")
    content_values['FirstName'] = query_content.get('FirstName', "")
    content_values['LastName'] = query_content.get('LastName', "")
    content_values['BirthCertificateID'] = query_content.get('BirthCertificateID', "")
    print(query_content)
    print(content_values)
    write_values['chfId'] = query_write.get('ID', "")
    write_values['FirstName'] = query_write.get('FirstName', "")
    write_values['LastName'] = query_write.get('LastName', "")
    write_values['BirthCertificateID'] = query_write.get('BirthCertificateID', "")

    variables = {
        'clientMutationLabel': f"Create insuree - {content_values['chfId']}",
        'chfId': f"{content_values['chfId']}",
        'lastName': f"{content_values['FirstName']}",
        'otherNames': f"{content_values['LastName']}",
        'genderId': 'M',
        'dob': '2000-06-20',
        'head': True,
        'cardIssued': False,
        'jsonExt': '{}',
    }

    result = client.execute(f'''
        query GetInsurees {{
            insurees(first: 1, chfId: "{content_values['chfId']}") {{
                edges{{
                    node{{
                        uuid
                    }}
                }}
            }}
        }}
        ''', context=context, variables=variables)

    insuree_data = result['data']['insurees']['edges'][0]['node']
    insuree_uuid = insuree_data['uuid']

    field_mapping = {
        "chfId": "chfId",
        "LastName": "lastName",
        "FirstName": "otherNames"
    }
    update_fields = "".join(f'{field_mapping[key]}: "{value}"'
                            for key, value in write_values.items()
                            if value and key in field_mapping)
    query = f'''
    mutation {{
      updateInsuree(
        input: {{
          clientMutationId: "552f8e55-ed5a-4e1e-a159-ea8f8cec0560"
          clientMutationLabel: "Update insuree"
          uuid: "{insuree_uuid}"
    {update_fields}
    genderId: "F"
    head: true
    dob: "1974-06-11"
    cardIssued:false
    familyId: 1
    relationshipId: 4
        }}
      ) {{
        clientMutationId
        internalId
      }}
    }}
    '''
    print(query)
    client.execute(query, context=context, variables=variables)

    response_data = {"status": 200}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(**read_record_schema)
@api_view(['POST'])
def get_single_record_from_registry(request, registryname, versionnumber):
    query_content = request.data.get('query', {}).get('content')

    if not query_content:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variable_definitions = ""
    variable_values = "first: 1, "
    variables = {}

    if 'ID' in query_content:
        variable_values += f'chfId: "{query_content["ID"]}",'
    if 'FirstName' in query_content:
        variable_values += f'otherNames: "{query_content["FirstName"]}",'
    if 'LastName' in query_content:
        variable_values += f'lastName: "{query_content["LastName"]}",'
    # if 'BirthCertificateID' in query_content:
    #     variable_values += ": $"
    variable_values = variable_values[:-1]

    print(f'''
    query GetInsurees   {{
        insurees({variable_values}) {{
            edges{{
                node{{
                    lastName
                    otherNames
                    chfId
                }}
            }}
        }}
    }}
    ''')
    result = client.execute(f'''
    query GetInsurees {{
        insurees({variable_values}) {{
            edges{{
                node{{
                    lastName
                    otherNames
                    chfId
                }}
            }}
        }}
    }}
    ''', context=context, variables=variables)
    insuree_data = result['data']['insurees']['edges'][0]['node']
    chfid = insuree_data['chfId']
    first_name = insuree_data['otherNames']
    other_names = insuree_data['lastName']

    if len(result['data']['insurees']['edges']) > 0:
        response_data = {
            "content": {
                "ID": chfid,
                "FirstName": first_name,
                "LastName": other_names
                # "BirthCertificateID":
            },
            "status": 200
        }
    else:
        response_data = {
            "detail": "no record found",
            "status": 404
        }

    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response



@api_view(['PUT'])
def update_multiple_records_in_registry(request, registryname, versionnumber):
    query_content = request.data.get('query', {}).get('content')
    query_write = request.data.get('query', {}).get('write')

    if not query_content and not query_write:
        status_code = 400

    client = Client(schema=Schema(query=Query, mutation=Mutation))
    context = QueryTest.BaseTestContext()
    context.user = None
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()

    content_values = write_values = {}

    # Variables to insert into the query.
    if 'ID' in query_content:
        content_values['chf_id'] = query_content['ID']
    if 'FirstName' in query_content:
        content_values['FirstName'] = query_content['FirstName']
    if 'LastName' in query_content:
        content_values['LastName'] = query_content['LastName']
    if 'BirthCertificateID' in query_content:
        content_values['BirthCertificateID'] = query_content['BirthCertificateID']

    if 'ID' in query_write:
        write_values['chf_id'] = query_write['ID']
    if 'FirstName' in query_write:
        write_values['FirstName'] = query_write['FirstName']
    if 'LastName' in query_write:
        write_values['LastName'] = query_write['LastName']
    if 'BirthCertificateID' in query_write:
        write_values['BirthCertificateID'] = query_write['BirthCertificateID']

    variables = {
        'clientMutationLabel': f"Create insuree - {content_values['chf_id']}",
        'chfId': f"{content_values['chf_id']}",
        'lastName': f"{content_values['first_name']}",
        'otherNames': f"{content_values['last_name']}",
        'genderId': 'M',
        'dob': '2000-06-20',
        'head': True,
        'cardIssued': False,
        'jsonExt': '{}',
    }

    # here get uuid to use it
    result = client.execute(f'''
          query GetInsurees {{
              insurees(chfId: "f"{content_values['chf_id']}") {{
                  edges{{
                      node{{
                          uuid
                      }}
                  }}
              }}
          }}
          ''', context=context, variables=variables)

    for single_record in result['data']['insurees']['edges']:
        query = f'''
          mutation {{
            updateInsuree(
              input: {{
                clientMutationLabel: "Update insuree - 070707093"
                uuid: "{single_record['uuid']}"
          chfId: "070707093"
          lastName: "Macintyre"
          otherNames: "Adele"
          genderId: "F"
          dob: "1974-06-11"
          head: false
          photo:{{
          id: 269
          uuid: "9cd0aee0-4d66-4cf2-b7ef-aa2f7fcfb7da"
          officerId: 3
          date: "2018-03-27"
          folder: "Images\\Updated\\"
          filename: "070707092_E00001_20180327_0.0_0.0.jpg"
        }}
          cardIssued:false
          familyId: 1
          relationshipId: 4
              }}
            ) {{
              clientMutationId
              internalId
            }}
          }}
          '''
        result = client.execute(query, context=context, variables=variables)

    response_data = {"status": 200}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@api_view(['POST'])
def update_or_create_record_in_registry(request, registryname, versionnumber):
    query_content = request.data.get('query', {}).get('content')
    query_write = request.data.get('query', {}).get('write')

    if not query_content and not query_write:
        status_code = 400

    client = Client(schema=Schema(query=Query, mutation=Mutation))
    context = QueryTest.BaseTestContext()
    context.user = None
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()


@api_view(['DELETE'])
def delete_record_in_registry():
    pass


@api_view(['GET'])
def get_record_field_value_from_registry():
    pass


@api_view(['GET'])
def get_personal_data_usage():
    pass
