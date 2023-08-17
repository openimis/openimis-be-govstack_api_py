from django.http import HttpResponse
from rest_framework.views import APIView


class PersonalDataAPI(APIView):
    def get(self, request):
        return HttpResponse(status=204)  # 204 No Content
