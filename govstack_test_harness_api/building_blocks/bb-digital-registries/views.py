from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from django.http import HttpResponse
import json

from insuree.models import Insuree
from .swaggers_schema import (
    create_request_body,
    create_response_body,
    get_multiple_records_from_registry_parameters,
    exists_request_body,
    exists_response_body
)
from .services import (
    check_if_registry_exists
)


@swagger_auto_schema(
    method='GET',
    operation_description="Creates a new record in the registry database.",
    manual_parameters=get_multiple_records_from_registry_parameters,
    responses={200: create_response_body},
)
@api_view(['GET'])
def get_multiple_records_from_registry(request, registryname, versionnumber):
    # Extract query parameters
    search = request.GET.get('search')
    filter = request.GET.get('filter')
    ordering = request.GET.get('ordering')
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    query_fieldname = request.GET.get('query.<fieldname>')

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
def create_new_record_in_registry():
    pass


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


    # SAMPLE CODE THAT USES GRAPHQL
    import requests
    from django.http import JsonResponse

    # Define the variables for the GraphQL query
    # variables = {
    #     "registryname": registryname,
    #     "versionnumber": versionnumber,
    #     "queryContent": query_content
    # }

    # Make a POST request to the GraphQL endpoint with the query and variables
    # graphql_url = 'http://localhost:8000/api/graphql'
    # graphql_query = '''
    #         query CheckIfRecordExists($firstName: String, $lastName: String) {
    #             insuree(firstName: $firstName, lastName: $lastName) {
    #                 exists
    #             }
    #         }
    #     '''
    # graphql_variables = {
    #     'firstName': request.data.get('query', {}).get('content', {}).get('FirstName'),
    #     'lastName': request.data.get('query', {}).get('content', {}).get('LastName')
    # }
    # graphql_data = {
    #     'query': graphql_query,
    #     'variables': graphql_variables
    # }
    #graphql_response = requests.post(graphql_url, json=graphql_data)
    # place where the code freeze^
    # graphql_result = graphql_response.json()

    # graphql_url = "http://localhost:8000/api/graphql"
    # response2 = requests.post(graphql_url)
    # # Check the response status code
    # if response.status_code != 200:
    #     return JsonResponse({"detail": "GraphQL request failed"}, status=500)

    # Parse the response JSON
    # data = response.json()
    # print(data)

    try:
        record_exists = check_if_registry_exists(registryname, versionnumber, query_content)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)

    if record_exists:
        message = "Object found from database"
    else:
        message = "Object not found from database"

    response_data = {
        "answer": {
            "status": record_exists,
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
