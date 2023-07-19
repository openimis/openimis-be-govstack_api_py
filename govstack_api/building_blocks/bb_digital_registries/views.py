from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse

from govstack_api.building_blocks.bb_digital_registries.swagger_schema import (
    create_request_body,
    create_response_body,
    get_multiple_records_from_registry_parameters,
    exists_request_body,
    exists_response_body, update_record_schema, read_record_schema, request_body_schema, responses_schema,
    create_or_update_response, read_value_parameters, read_value_response_body, delete_parameters, delete_response
)


@swagger_auto_schema(
    method='GET',
    operation_description="Creates a new record in the registry database.",
    manual_parameters=get_multiple_records_from_registry_parameters,
    responses={200: create_response_body},
)
@api_view(['GET'])
def get_multiple_records_from_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(
    method='post',
    operation_description="Create new record",
    request_body=create_request_body,
    responses={200: create_response_body},
)
@api_view(['POST'])
def create_new_record_in_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(
    method='post',
    operation_description="Searches records based on input parameters and returns boolean answer (true/false).",
    request_body=exists_request_body,
    responses={200: exists_response_body},
)
@api_view(['POST'])
def check_if_record_exists_in_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(**update_record_schema)
@api_view(['PUT'])
def update_single_record_in_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(**read_record_schema)
@api_view(['POST'])
def get_single_record_from_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content




@swagger_auto_schema(
    method='put',
    operation_description='Updates multiple records in the registry database that match the input query.',
    request_body=request_body_schema,
    responses=responses_schema
)
@api_view(['PUT'])
def update_multiple_records_in_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(
    method='post',
    operation_description='''API updates existing record if matching with input parameters is
        successful. If record is not found the API will create a new record.''',
    request_body=request_body_schema,
    responses=create_or_update_response
)
@api_view(['POST'])
def update_or_create_record_in_registry(request, registryname, versionnumber):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(
    method='delete',
    operation_description='Delete record.',
    manual_parameters=delete_parameters,
    responses={204: delete_response},
)
@api_view(['DELETE'])
def delete_record_in_registry(request, registryname, versionnumber, ID):
    return HttpResponse(status=204)  # 204 No Content


@swagger_auto_schema(
    method='get',
    operation_description='Searches and returns one record’s one field value.',
    manual_parameters=read_value_parameters,
    responses={200: read_value_response_body},
)
@api_view(['GET'])
def get_record_field_value_from_registry(request, registryname, versionnumber, uuid, field, ext):
    return HttpResponse(status=204)  # 204 No Content


@api_view(['GET'])
def get_personal_data_usage():
    return HttpResponse(status=204)  # 204 No Content



