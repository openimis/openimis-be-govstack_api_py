from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .controllers.single_record_controllers import get_single_record_controller
from .serializers import InsureeSerializer, QueryValidatorSerializer

from govstack_api.building_blocks.bb_digital_registries.serializers import InsureeSerializer
from govstack_api.building_blocks.bb_digital_registries.swagger_schema import (
    create_request_body,
    create_response_body,
    get_multiple_records_from_registry_parameters,
    exists_request_body, info_mediator_client,
    exists_response_body, update_record_schema, read_record_schema, request_body_schema, responses_schema,
    create_or_update_response, read_value_parameters, read_value_response_body, delete_parameters, delete_response,
    response_200_body
)
from ...middleware import middleware_marker


class SingleRecordAPI(APIView):
    @swagger_auto_schema(
        operation_description='Searches and returns one record’s one field value.',
        manual_parameters=read_value_parameters,
        responses={200: read_value_response_body},
    )
    def get(self, request, registryname, versionnumber, uuid, field, ext):
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Create new record",
        request_body=create_request_body,
        responses={200: create_response_body},
    )
    def post(self, request, registryname, versionnumber):
        return HttpResponse(status=204)  # 204 No Content

    @swagger_auto_schema(**update_record_schema)
    def put(self, request, registryname, versionnumber):
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description='Delete record.',
        manual_parameters=delete_parameters,
        responses={204: delete_response},
    )
    def delete(self, request, registryname, versionnumber, ID):
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchRecordView(APIView):

    @middleware_marker
    @swagger_auto_schema(
        operation_description="Read single record from registry.",
        request_body=exists_request_body,
        manual_parameters=[info_mediator_client],
        responses={200: response_200_body},
    )
    def post(self, request, registryname, versionnumber):
        serializer = QueryValidatorSerializer(data=request.data)
        if serializer.is_valid():
            status_code = get_single_record_controller(request, serializer.data, registryname, versionnumber)
            # handle other errors
            if status_code == 200:
                # send response that matches scheme
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckRecordExistsView(APIView):
    @swagger_auto_schema(
        operation_description="Searches records based on input parameters and returns boolean answer (true/false).",
        request_body=exists_request_body,
        responses={200: exists_response_body},
    )
    def post(self, request, registryname, versionnumber):
        # check if record exists
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateOrCreateRecordView(APIView):
    @swagger_auto_schema(
        operation_description='''API updates existing record if matching with input parameters is
            successful. If record is not found the API will create a new record.''',
        request_body=request_body_schema,
        responses=create_or_update_response
    )
    def post(self, request, registryname, versionnumber):
        return Response(status=status.HTTP_204_NO_CONTENT)


class MultipleRecordAPI(APIView):

    @swagger_auto_schema(
        operation_description="Creates a new record in the registry database.",
        manual_parameters=get_multiple_records_from_registry_parameters,
        responses={200: create_response_body})
    def get(self, request, registryname, versionnumber):
        return HttpResponse(status=204)  # 204 No Content

    @swagger_auto_schema(
        operation_description='Updates multiple records in the registry database that match the input query.',
        request_body=request_body_schema,
        responses=responses_schema
    )
    def put(self, request, registryname, versionnumber):
        return HttpResponse(status=204)  # 204 No Content


class PersonalDataAPI(APIView):
    def get(self, request):
        return HttpResponse(status=204)  # 204 No Content

