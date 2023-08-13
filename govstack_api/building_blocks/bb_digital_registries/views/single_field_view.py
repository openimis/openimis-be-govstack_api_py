from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from govstack_api.building_blocks.bb_digital_registries.controllers.single_record_controllers import \
    get_single_record_field_controller
from govstack_api.building_blocks.bb_digital_registries.serializers import SingleRecordSerializer
from govstack_api.building_blocks.bb_digital_registries.swagger_schema import read_value_parameters, \
    read_value_response_body
from govstack_api.building_blocks.bb_digital_registries.views import handle_mutation_exceptions
from govstack_api.middleware import authenticate_decorator


@method_decorator(authenticate_decorator, name='dispatch')
class SingleFieldView(APIView):
    @swagger_auto_schema(
        operation_description='Searches and returns one record’s one field value.',
        manual_parameters=read_value_parameters,
        responses={200: read_value_response_body},
    )
    @handle_mutation_exceptions()
    def get(self, request, registryname, versionnumber, uuid, field, ext):
        serializer = SingleRecordSerializer(data={
            'registryname': registryname,
            'versionnumber': versionnumber,
            'uuid': uuid,
            'field': field,
            'ext': ext
        })
        if serializer.is_valid(raise_exception=True):
            status_code, registry_record_field = get_single_record_field_controller(
                request, serializer.data, registryname, versionnumber
            )
            if status_code == 200:
                return Response(registry_record_field, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status_code)
        return Response(status=status.HTTP_400_BAD_REQUEST)
