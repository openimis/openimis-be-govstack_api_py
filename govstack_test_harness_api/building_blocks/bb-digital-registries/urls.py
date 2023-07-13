from django.urls import path
from .views.check_if_record_exists_in_registry import check_if_record_exists_in_registry


urlpatterns = [
    path('data/<str:registryname>/<str:versionnumber>/exists', check_if_record_exists_in_registry)
]