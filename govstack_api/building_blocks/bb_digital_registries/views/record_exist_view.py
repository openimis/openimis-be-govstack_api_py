from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from govstack_api.building_blocks.bb_digital_registries.controllers.single_record_controllers import \
    check_record_presence_controller
from govstack_api.building_blocks.bb_digital_registries.serializers import QueryValidatorSerializer
from govstack_api.building_blocks.bb_digital_registries.swagger_schema import exists_request_body, exists_response_body
from govstack_api.building_blocks.bb_digital_registries.views import handle_mutation_exceptions


class CheckRecordPresenceView(APIView):
    @swagger_auto_schema(
        operation_description="Searches records based on input parameters and returns boolean answer (true/false).",
        request_body=exists_request_body,
        responses={200: exists_response_body},
    )
    @handle_mutation_exceptions()
    def post(self, request, registryname, versionnumber):
        serializer = QueryValidatorSerializer(data=request.data)
        if serializer.is_valid():
            status_code, record_exists = check_record_presence_controller(
                request, serializer.data, registryname, versionnumber
            )
            message = "Object found from database" if record_exists else "Object not found from database"
            return Response({
                "answer": {
                    "status": record_exists,
                    "message": message}},
                status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
