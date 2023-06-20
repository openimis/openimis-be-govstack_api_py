from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('govstack_test_harness_api_py.building_blocks.bb-digital-registries.urls')),
]