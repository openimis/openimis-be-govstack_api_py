from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from govstack_api.building_blocks.bb_digital_registries.controllers.single_record_controllers import \
    get_single_record_field_controller, create_single_record_controller, update_single_record_controller, \
    delete_record_controller
from govstack_api.building_blocks.bb_digital_registries.registries.registry_qgl_utils import MutationError
from govstack_api.building_blocks.bb_digital_registries.serializers import SingleRecordSerializer, \
    WriteValidatorSerializer, CombinedValidatorSerializer, RegistryDeleteSerializer
from govstack_api.building_blocks.bb_digital_registries.swagger_schema import read_value_parameters, \
    read_value_response_body, create_request_body, create_response_body, request_body_schema, delete_parameters, \
    delete_response
from govstack_api.building_blocks.bb_digital_registries.views import handle_mutation_exceptions


class SingleRecordAPI(APIView):

    @swagger_auto_schema(
        operation_description="Create new record",
        request_body=create_request_body,
        responses={200: create_response_body},
    )
    @handle_mutation_exceptions()
    def post(self, request, registryname, versionnumber):
        serializer = WriteValidatorSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            status_code, registry_record = create_single_record_controller(
                request, serializer.data, registryname, versionnumber
            )
            if status_code == 200:
                return Response(registry_record, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status_code)
        except MutationError as e:
            return Response(e.detail, 400)
        except ValidationError as e:
            return Response(e.detail, status=e.status_code)

    @swagger_auto_schema(
        operation_description="Updates one existing record in the registry database.",
        request_body=request_body_schema,
        responses={200: 'Successful update or creation'})
    @handle_mutation_exceptions()
    def put(self, request, registryname, versionnumber):
        serializer = CombinedValidatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_code = update_single_record_controller(request, serializer.data, registryname, versionnumber)
        if status_code == 200:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.data, status=status_code)

    @swagger_auto_schema(
        operation_description='Delete record.',
        manual_parameters=delete_parameters,
        responses={204: delete_response},
    )
    @handle_mutation_exceptions()
    def delete(self, request, registryname, versionnumber, ID):
        serializer = RegistryDeleteSerializer(data={
            'registryname': registryname,
            'versionnumber': versionnumber,
            'ID': ID
        })
        serializer.is_valid(raise_exception=True)
        status_code = delete_record_controller(request, serializer.data, registryname, versionnumber)
        if status_code == 204:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.data, status=status_code)
