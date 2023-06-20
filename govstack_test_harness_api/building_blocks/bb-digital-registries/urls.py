from django.urls import path
from .views import getDataFromSubFolder, get_registry_data

urlpatterns = [
    path('bbdr/', getDataFromSubFolder, name='digital_registries'),
    path('data/<str:registryname>/<str:versionnumber>/exists', get_registry_data, name='data_registry'),
]