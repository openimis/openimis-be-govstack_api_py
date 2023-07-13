from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..serializers.record_exists_serializer import RecordExistsSerializer
from drf_yasg.utils import swagger_auto_schema
from .swaggers_schema import exists_request_body, exists_response_body
from ..services.services import login_with_env_variables
from ..controllers.record_exists_controller import check_if_record_exists


@swagger_auto_schema(
    method='post',
    operation_description="Searches records based on input parameters and returns boolean answer (true/false).",
    request_body=exists_request_body,
    responses={200: exists_response_body},
)
@api_view(['POST'])
def check_if_record_exists_in_registry(request, registryname, versionnumber):
    # This is controller logic: receiving the request and validating input
    data = request.data
    data.update({"registryname": registryname, "versionnumber": versionnumber})
    serializer = RecordExistsSerializer(data=data)
    if serializer.is_valid():
        context = login_with_env_variables(request)
        response_data = check_if_record_exists(
            serializer.validated_data,
            request.COOKIES.get('JWT'),
            context
        )
        return JsonResponse(response_data)
    else:
        return JsonResponse(serializer.errors, status=400)
