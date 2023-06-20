from django.urls import path, include
from . import views
import govstack_test_harness_api

urlpatterns = [
    path('', include('govstack_test_harness_api.building_blocks.bb-digital-registries.urls')),
]