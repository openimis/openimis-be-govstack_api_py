from django.urls import path
from .views import (
    get_multiple_records_from_registry,
    create_new_record_in_registry,
    check_if_record_exists_in_registry,
    update_single_record_in_registry,
    update_multiple_records_in_registry,
    update_or_create_record_in_registry,
    delete_record_in_registry,
    get_record_field_value_from_registry,
    get_personal_data_usage,
    get_single_record_from_registry,
)

urlpatterns = [
    path('data/<str:registryname>/<str:versionnumber>', get_multiple_records_from_registry),
    path('data/<str:registryname>/<str:versionnumber>/create', create_new_record_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/exists', check_if_record_exists_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/read', get_single_record_from_registry),
    path('data/<str:registryname>/<str:versionnumber>/update', update_single_record_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/update-entries', update_multiple_records_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/update-or-create', update_or_create_record_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/<str:ID>/delete', delete_record_in_registry),
    path('data/<str:registryname>/<str:versionnumber>/<str:uuid>/read-value/<str:field>.<ext>',
         get_record_field_value_from_registry),
    path('data/myPersonalDataUsage/1.0', get_personal_data_usage),
]