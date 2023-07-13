from django.urls import path
# from .views.get_multiple_records_from_registry import get_multiple_records_from_registry
# from .views.create_new_record_in_registry import create_new_record_in_registry
# from .views.update_single_record_in_registry import update_single_record_in_registry
# from .views.update_multiple_records_in_registry import update_multiple_records_in_registry
# from .views.update_or_create_record_in_registry import update_or_create_record_in_registry
# from .views.delete_record_in_registry import delete_record_in_registry
# from .views.get_record_field_value_from_registry import get_record_field_value_from_registry
# from .views.get_personal_data_usage import get_personal_data_usage
# from .views.get_single_record_from_registry import get_single_record_from_registry
# from .views.login_view import login_view
from .views.check_if_record_exists_in_registry import check_if_record_exists_in_registry


urlpatterns = [
    # path('data/<str:registryname>/<str:versionnumber>', get_multiple_records_from_registry),
    # path('data/<str:registryname>/<str:versionnumber>/create', create_new_record_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/exists', check_if_record_exists_in_registry)
    # path('data/<str:registryname>/<str:versionnumber>/read', get_single_record_from_registry),
    # path('data/<str:registryname>/<str:versionnumber>/update', update_single_record_in_registry),
    # path('data/<str:registryname>/<str:versionnumber>/update-entries', update_multiple_records_in_registry),
    # path('data/<str:registryname>/<str:versionnumber>/update-or-create', update_or_create_record_in_registry),
    # path('data/<str:registryname>/<str:versionnumber>/<str:ID>/delete', delete_record_in_registry),
    # path('data/<str:registryname>/<str:versionnumber>/<str:uuid>/read-value/<str:field>.<ext>',
    #      get_record_field_value_from_registry),
    # path('data/myPersonalDataUsage/1.0', get_personal_data_usage),
    # path('login/', login_view)
]