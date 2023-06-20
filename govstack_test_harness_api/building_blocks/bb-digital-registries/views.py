from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from django.http import HttpResponse
import json

@api_view(['GET'])
def getDataFromSubFolder(request):
    person = {'registry':'John', 'ID':'7312'}
    return Response(person)


@api_view(['GET', 'POST'])
@csrf_exempt
def get_registry_data(request, registryname, versionnumber):
    # Extract query parameters
    search = request.GET.get('search')
    filter = request.GET.get('filter')
    ordering = request.GET.get('ordering')
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    query_fieldname = request.GET.get('query.<fieldname>')

    # Logic to retrieve data from your database and filter/order as required
    # For demonstration purposes, let's say you have created a list named 'data'
    data = [...]  # replace this with your logic to fetch data from the database

    # Apply pagination
    paginator = Paginator(data, page_size)
    current_page = paginator.get_page(page)

    print("Sample message")

    status = False  # Przykład, ustaw status na True lub False w zależności od twojej logiki.
    message = "Object found from database" # Przykład, ustaw odpowiednią wiadomość.

    # Konstrukcja danych odpowiedzi zgodnie ze schematem
    response_data = {
        "answer": {
            "status": status,
            "message": message
        }
    }

    # Utworzenie odpowiedzi JSON i zwrócenie jej
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    # return HttpResponse(json.dumps(response_data), content_type="application/json; charset=utf-8")
    # return JsonResponse(response_data)


@api_view(['GET', 'POST'])
@csrf_exempt
def get_registry_data2(request, registryname, versionnumber):
    # Extract query parameters
    search = request.GET.get('search')
    filter = request.GET.get('filter')
    ordering = request.GET.get('ordering')
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    query_fieldname = request.GET.get('query.<fieldname>')

    # Logic to retrieve data from your database and filter/order as required
    # For demonstration purposes, let's say you have created a list named 'data'
    data = [...]  # replace this with your logic to fetch data from the database

    # Apply pagination
    paginator = Paginator(data, page_size)
    current_page = paginator.get_page(page)

    print("Sample message")

    status = True  # Przykład, ustaw status na True lub False w zależności od twojej logiki.
    message = "Object found from database" # Przykład, ustaw odpowiednią wiadomość.

    # Konstrukcja danych odpowiedzi zgodnie ze schematem
    response_data = {
        "answer": {
            "status": status,
            "message": message
        }
    }

    # Utworzenie odpowiedzi JSON i zwrócenie jej
    return Response({"status": True})
