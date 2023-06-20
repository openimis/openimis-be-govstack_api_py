from django.urls import path
from .views import getDataFromSubFolder, get_registry_data, get_registry_data2

urlpatterns = [
    path('bbdr/', getDataFromSubFolder, name='digital_registries'),
    path('data/<str:registryname>/<str:versionnumber>/exists', get_registry_data, name='data_registry'),
    path('data/<str:registryname>/<str:versionnumber>/exists2', get_registry_data2, name='data_registry2'),
]