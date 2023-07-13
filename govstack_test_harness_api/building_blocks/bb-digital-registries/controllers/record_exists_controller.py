from ..services.record_exists_service import RecordExistsService
from ..services.services import get_query_content_values, login_with_env_variables


def check_if_record_exists(data, jwt, context):
    content_values = get_query_content_values(data['query']['content'], data['registryname'], data['versionnumber'])
    service = RecordExistsService(
        jwt,
        context=context,
        validated_data=data,
    )
    return service.execute()