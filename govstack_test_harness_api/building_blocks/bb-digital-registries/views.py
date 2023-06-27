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
from contribution_plan.tests.gql_tests.query_tests import *
from graphene import Schema
from .swaggers_schema import (
    create_request_body,
    create_response_body,
    get_multiple_records_from_registry_parameters,
    exists_request_body,
    exists_response_body
)
from .services import (
    check_if_registry_exists,
    QueryTest
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

    client = Client(schema=Schema(query=Query, mutation=Mutation))
    context = QueryTest.BaseTestContext()
    context.user = None
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()

    variable_definitions = ""
    variable_values = "first: 1, "
    variables = {}
    if ordering == "descending":
        ordering = f"-{filter}"
    else:
        ordering = filter
    result = client.execute(f'''
        query GetInsurees {{
            insurees(orderBy: "{ordering}", {filter}:{search} ) {{
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


    filters = []
    if filter == 'FirstName':
        filters.append(Q(other_names=search))
    if filter == 'LastName':
        filters.append(Q(last_name=search))
    if filter == 'ID':
        filters.append(Q(id=search))
    if filter == 'BirthCertificateID':
        filters.append(Q(json_ext=search))
    data = Insuree.objects.filter(*filters).all()

    paginator = Paginator(data, page_size)
    current_page = paginator.get_page(page)

    if query_fieldname and query_fieldname != 'results':
        try:
            Insuree._meta.get_field(query_fieldname)  # Check if the field exists in the Insuree model
        except FieldDoesNotExist:
            response_data = {
                "error": f"The field '{query_fieldname}' does not exist."
            }
            response = HttpResponse(json.dumps(response_data))
            response['Content-Type'] = "application/json; charset=utf-8"
            response.status_code = 400  # Bad Request
            return response

        data = data.values_list(query_fieldname, flat=True)

    response_data = {
        "count": current_page.paginator.count,
        "next": current_page.next_page_number() if current_page.has_next() else None,
        "previous": current_page.previous_page_number() if current_page.has_previous() else None,
        "results": list(data)  # Convert queryset or field values to a list
    }

    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(
    method='post',
    operation_description="Creates a new record in the registry database.",
    request_body=create_request_body,
    responses={200: create_response_body},
)
@api_view(['POST'])
def create_new_record_in_registry(request, registryname, versionnumber):
    query_content = request.data.get('query', {}).get('content')

    if not query_content:
        status_code = 400

    client = Client(schema=Schema(query=Query, mutation=Mutation))
    context = QueryTest.BaseTestContext()
    context.user = None
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()

    # Variables to insert into the query.
    if 'ID' in query_content:
        chf_id = query_content['ID']
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
                clientMutationId: "{variables['clientMutationId']}"
                clientMutationLabel: "{variables['clientMutationLabel']}"
                chfId: "{variables['chfId']}"
                lastName: "{variables['lastName']}"
                otherNames: "{variables['otherNames']}"
                genderId: "{variables['genderId']}"
                dob: "{variables['dob']}"
                head: {str(variables['head']).lower()}
                cardIssued: {str(variables['cardIssued']).lower()}
                jsonExt: "{variables['jsonExt']}"
            }}
        ) {{
            clientMutationId
            internalId
        }}
    }}
    '''
    result = client.execute(query, context=context, variables=variables)

    # get single record from registry by chfID

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

    client = Client(schema=Schema(query=Query, mutation=Mutation))
    context = QueryTest.BaseTestContext()
    context.user = None
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()

    variable_definitions = ""
    variable_values = "first: 1, "
    variables = {}

    # if 'ID' in query_content:
    #     variable_definitions += "$ID: String!"
    #     variable_values += "id: $ID"
    if 'FirstName' in query_content:
        variable_definitions += "$otherNames: String!,"
        variable_values += "otherNames: $otherNames,"
        variables["otherNames"] = query_content["FirstName"]
    if 'LastName' in query_content:
        variable_definitions += "$lastName: String!,"
        variable_values += "lastName: $lastName,"
    # if 'BirthCertificateID' in query_content:
    #     variable_definitions += "$: "
    #     variable_values += ": $"
    variable_definitions = variable_definitions[:-1]
    variable_values = variable_values[:-1]

    result = client.execute(f'''
    query GetInsurees({variable_definitions}) {{
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

@api_view(['PUT'])
def update_single_record_in_registry():
    pass


@api_view(['POST'])
def get_single_record_from_registry():
    pass


@api_view(['PUT'])
def update_multiple_records_in_registry():
    pass


@api_view(['POST'])
def update_or_create_record_in_registry():
    pass


@api_view(['DELETE'])
def delete_record_in_registry():
    pass


@api_view(['GET'])
def get_record_field_value_from_registry():
    pass


@api_view(['GET'])
def get_personal_data_usage():
    pass
