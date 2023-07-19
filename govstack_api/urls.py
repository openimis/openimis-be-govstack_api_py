from django.urls import path, include

urlpatterns = [
    path('', include('govstack_api.building_blocks.bb_digital_registries.urls')),
]