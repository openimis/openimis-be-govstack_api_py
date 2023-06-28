from drf_yasg.utils import swagger_auto_schema
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from django.http import HttpResponse
import json
from insuree.schema import Query, Mutation
from graphene import Schema

from .swaggers_schema import (
    create_request_body,
    create_response_body,
    get_multiple_records_from_registry_parameters,
    exists_request_body,
    exists_response_body, update_record_schema, read_record_schema, request_body_schema, responses_schema,
    create_or_update_response, read_value_parameters, read_value_response_body, delete_parameters, delete_response
)
from .services import (
    get_client, get_context, get_update_registry_query, get_insurees_query, get_query_content_values,
    get_query_write_values, get_values_for_insurees, get_search_insurees_arguments, get_update_fields,
    create_insurees_query, delete_insuree_query
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
    write_values = get_query_write_values(request.data.get('write', {}).get('content'))
    if not write_values:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variables = get_values_for_insurees(write_values)
    query = create_insurees_query(variables)

    client.execute(query, context=context, variables=variables)
    response_data = {
        "content": {
            "ID": f"{write_values['chfId']}",
            "FirstName": f"{write_values['otherNames']}",
            "LastName": f"{write_values['lastName']}",
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
    content_values = get_query_content_values(request.data.get('query', {}).get('content'))
    if not content_values:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variables = get_values_for_insurees(content_values)
    variable_values = get_search_insurees_arguments(content_values)
    query = get_insurees_query(variable_values, "lastName")
    result = client.execute(query, context=context, variables=variables)
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
    content_values = get_query_content_values(request.data.get('query', {}).get('content'))
    write_values = get_query_write_values(request.data.get('write', {}).get('content'))
    if not content_values and not write_values:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variables = get_values_for_insurees(content_values)

    result = client.execute(f'''
        query GetInsurees {{
            insurees(first: 1, chfId: "{content_values['chfId']}") {{
                edges{{
                    node{{
                        uuid
                        chfId
                    }}
                }}
            }}
        }}
        ''', context=context, variables=variables)
    insuree_data = result['data']['insurees']['edges'][0]['node']
    insuree_uuid = insuree_data['uuid']

    update_fields = get_update_fields(write_values)
    query = get_update_registry_query(
        insuree_data['uuid'],
        insuree_data['chfId'],
        update_fields
    )
    client.execute(query, context=context, variables=variables)

    response_data = {"status": 200}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(**read_record_schema)
@api_view(['POST'])
def get_single_record_from_registry(request, registryname, versionnumber):
    content_values = get_query_content_values(request.data.get('query', {}).get('content'))

    if not content_values:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variable_values = get_search_insurees_arguments(content_values)
    query = get_insurees_query(variable_values, "lastName otherNames chfId")
    result = client.execute(query, context=context)

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


@swagger_auto_schema(
    method='put',
    operation_description='Updates multiple records in the registry database that match the input query.',
    request_body=request_body_schema,
    responses=responses_schema
)
@api_view(['PUT'])
def update_multiple_records_in_registry(request, registryname, versionnumber):
    content_values = get_query_content_values(request.data.get('query', {}).get('content'))
    write_values = get_query_write_values(request.data.get('write', {}).get('content'))
    if not content_values and not write_values:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variables = get_values_for_insurees(content_values)

    variable_values = get_search_insurees_arguments(content_values)

    query = get_insurees_query(variable_values, "uuid chfId")
    result = client.execute(query, context=context, variables=variables)

    update_fields = get_update_fields(write_values)

    for single_record in result['data']['insurees']['edges']:
        query = get_update_registry_query(
            single_record['node']['uuid'],
            single_record['node']['chfId'],
            update_fields
        )
        client.execute(query, context=context, variables=variables)

    response_data = {"status": 200}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(
    method='post',
    operation_description='''API updates existing record if matching with input parameters is
        successful. If record is not found the API will create a new record.''',
    request_body=request_body_schema,
    responses=create_or_update_response
)
@api_view(['POST'])
def update_or_create_record_in_registry(request, registryname, versionnumber):
    content_values = get_query_content_values(request.data.get('query', {}).get('content'))
    write_values = get_query_write_values(request.data.get('write', {}).get('content'))

    if not content_values or not write_values:
        status_code = 400

    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    variables = get_values_for_insurees(content_values)
    variable_values = get_search_insurees_arguments(content_values)
    query = get_insurees_query(variable_values, "uuid chfId")
    result = client.execute(query, context=context, variables=variables)

    insuree_data = result['data']['insurees']['edges'][0]['node']
    if insuree_data:
        query = get_update_registry_query(
            insuree_data['uuid'],
            insuree_data['chfId'],
            get_update_fields(write_values)
        )
    else:
        query = create_insurees_query(variables)
    client.execute(query, context=context, variables=variables)

    response_data = {"status": 200}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response

@swagger_auto_schema(
    method='delete',
    operation_description='Delete record.',
    manual_parameters=delete_parameters,
    responses={204: delete_response},
)
@api_view(['DELETE'])
def delete_record_in_registry(request, registryname, versionnumber, ID):
    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    query = get_insurees_query(f'chfId: "{ID[:12]}"', "uuid")
    result = client.execute(query, context=context)

    insuree_data = result['data']['insurees']['edges'][0]['node']
    if insuree_data:
        query = delete_insuree_query(insuree_data['uuid'])
    client.execute(query, context=context)

    response_data = {"status": 204}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response


@swagger_auto_schema(
    method='get',
    operation_description='Searches and returns one record’s one field value.',
    manual_parameters=read_value_parameters,
    responses={200: read_value_response_body},
)
@api_view(['GET'])
def get_record_field_value_from_registry(
        request,
        registryname,
        versionnumber,
        uuid,
        field,
        ext
):
    client = get_client(Schema, Query, Mutation)
    context = get_context(request)

    query = get_insurees_query(f'chfId: "{uuid}"', f"{field}")
    result = client.execute(query, context=context)

    insuree_data = result['data']['insurees']['edges'][0]['node']

    if isinstance(insuree_data[field], str):
        response_data = insuree_data[field]
    else:
        response_data = {"value": insuree_data[field]}
    response = HttpResponse(json.dumps(response_data))
    response['Content-Type'] = "application/json; charset=utf-8"
    return response

@api_view(['GET'])
def get_personal_data_usage():
    response_data = {"error": "Resource not found"}
    response = HttpResponse(json.dumps(response_data), status=404)
    response['Content-Type'] = "application/json; charset=utf-8"
    return response
