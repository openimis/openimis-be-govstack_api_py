from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('openimis-be-govstack_test_harness_api.building_blocks.bb-digital-registries.urls')),
]