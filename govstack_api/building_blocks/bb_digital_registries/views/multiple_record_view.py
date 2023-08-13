from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from govstack_api.building_blocks.bb_digital_registries.controllers.multiple_record_controllers import \
    ListViewController, update_multiple_records_controller
from govstack_api.building_blocks.bb_digital_registries.serializers import MultipleRecordsSerializer, \
    CombinedValidatorSerializer
from govstack_api.building_blocks.bb_digital_registries.swagger_schema import \
    get_multiple_records_from_registry_parameters, create_response_body, request_body_schema, responses_schema
from govstack_api.building_blocks.bb_digital_registries.views import handle_mutation_exceptions


class MultipleRecordAPI(APIView):

    @swagger_auto_schema(
        operation_description="Get records from the registry database.",
        manual_parameters=get_multiple_records_from_registry_parameters,
        responses={200: create_response_body})
    @handle_mutation_exceptions()
    def get(self, request, registryname, versionnumber):
        data = {
            'registryname': registryname,
            'versionnumber': versionnumber,
        }
        if search := request.query_params.get('search'):
            data['search'] = search
        if filter := request.query_params.get('filter'):
            data['filter'] = filter
        if ordering := request.query_params.get('ordering'):
            data['ordering'] = ordering
        if page := request.query_params.get('page'):
            data['page'] = page
        if fieldname := request.query_params.get('query.<fieldname>'):
            data['fieldname'] = fieldname
        if page_size := request.query_params.get('page_size'):
            data['page_size'] = page_size

        serializer = MultipleRecordsSerializer(data=data)

        if serializer.is_valid():
            status_code, list_of_records = ListViewController(
                request, registryname, versionnumber,
            ).get_records(serializer.data)

            return Response(list_of_records, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='Updates multiple records in the registry database that match the input query.',
        request_body=request_body_schema,
        responses=responses_schema
    )
    @handle_mutation_exceptions()
    def put(self, request, registryname, versionnumber):
        # TODO: This will always fail. According to the documentation, it's labeled as PUT in the API schema, but it
        #  most likely should be PATCH. There's a unique ID constraint that contradicts the expected PUT structure.

        serializer = CombinedValidatorSerializer(data=request.data)
        if serializer.is_valid():
            status_code = update_multiple_records_controller(
                request, serializer.data, registryname, versionnumber
            )
            if status_code == 200:
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status_code)
        return Response(status=status.HTTP_400_BAD_REQUEST)
