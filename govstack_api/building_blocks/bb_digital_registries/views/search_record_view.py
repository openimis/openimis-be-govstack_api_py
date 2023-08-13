from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from govstack_api.building_blocks.bb_digital_registries.controllers.single_record_controllers import \
    read_single_record_controller
from govstack_api.building_blocks.bb_digital_registries.serializers import QueryValidatorSerializer
from govstack_api.building_blocks.bb_digital_registries.swagger_schema import exists_request_body, info_mediator_client, \
    response_200_body
from govstack_api.building_blocks.bb_digital_registries.views import handle_mutation_exceptions
from govstack_api.middleware import authenticate_decorator


@method_decorator(authenticate_decorator, name='dispatch')
class SearchRecordView(APIView):

    @swagger_auto_schema(
        operation_description="Read single record from registry.",
        request_body=exists_request_body,
        manual_parameters=[info_mediator_client],
        responses={200: response_200_body},
    )
    @handle_mutation_exceptions()
    def post(self, request, registryname, versionnumber):
        serializer = QueryValidatorSerializer(data=request.data)
        if serializer.is_valid():
            status_code, registry_record = read_single_record_controller\
                (request, serializer.data, registryname, versionnumber)
            if status_code == 200:
                return_data = {'content': registry_record}
                return Response(return_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


