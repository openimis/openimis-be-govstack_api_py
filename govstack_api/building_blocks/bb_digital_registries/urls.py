from django.urls import path
from .views import (
    SearchRecordView, SingleRecordAPI,
    CheckRecordPresenceView, UpdateOrCreateRecordView,
    MultipleRecordAPI, PersonalDataAPI
)

urlpatterns = [
    path('data/<str:registryname>/<str:versionnumber>/create', SingleRecordAPI.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/exists', CheckRecordPresenceView.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/read', SearchRecordView.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/update', SingleRecordAPI.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/update-or-create', UpdateOrCreateRecordView.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/<str:ID>/delete', SingleRecordAPI.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/<str:uuid>/read-value/<str:field>.<ext>',
         SingleRecordAPI.as_view()),
    path('data/<str:registryname>/<str:versionnumber>', MultipleRecordAPI.as_view()),
    path('data/<str:registryname>/<str:versionnumber>/update-entries', MultipleRecordAPI.as_view()),
    path('data/myPersonalDataUsage/1.0', PersonalDataAPI.as_view()),
]