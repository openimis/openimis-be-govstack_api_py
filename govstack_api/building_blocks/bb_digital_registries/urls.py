from django.urls import path

from govstack_api.building_blocks.bb_digital_registries.views import PersonalDataAPI
from govstack_api.building_blocks.bb_digital_registries.views import MultipleRecordAPI
from govstack_api.building_blocks.bb_digital_registries.views import UpdateOrCreateRecordView
from govstack_api.building_blocks.bb_digital_registries.views import CheckRecordPresenceView
from govstack_api.building_blocks.bb_digital_registries.views import SearchRecordView
from govstack_api.building_blocks.bb_digital_registries.views import SingleRecordAPI
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('data/<str:registryname>/<str:versionnumber>/create', SingleRecordAPI.as_view(), name="create_registry_record"),
    path('data/<str:registryname>/<str:versionnumber>/exists', CheckRecordPresenceView.as_view(), name="check_registry_record_presence"),
    path('data/<str:registryname>/<str:versionnumber>/read', SearchRecordView.as_view(), name="read_registry_record"),
    path('data/<str:registryname>/<str:versionnumber>/update', SingleRecordAPI.as_view(), name="update_registry_record"),
    path('data/<str:registryname>/<str:versionnumber>/update-or-create', UpdateOrCreateRecordView.as_view(), name="update_or_create_registry_record"),
    path('data/<str:registryname>/<str:versionnumber>/<str:ID>/delete', SingleRecordAPI.as_view(), name="delete_registry_record"),
    path('data/<str:registryname>/<str:versionnumber>/<str:uuid>/read-value/<str:field>.<ext>',
         SingleRecordAPI.as_view(), name="read_field_from_registry_record"),
    path('data/<str:registryname>/<str:versionnumber>', MultipleRecordAPI.as_view(), name="list_registry_records"),
    path('data/<str:registryname>/<str:versionnumber>/update-entries', MultipleRecordAPI.as_view(), name="update_registry_records"),
    path('data/myPersonalDataUsage/1.0', PersonalDataAPI.as_view(), name="get_personal_data"),
    path('docs/', SpectacularAPIView.as_view(), name='docs'),
    path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='docs'), name='redoc'),
]