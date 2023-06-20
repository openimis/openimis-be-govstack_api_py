from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework.decorators import api_view

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

    # Construct the response
    response = {
        "count": paginator.count,
        "next": None if not current_page.has_next() else f"?page={current_page.next_page_number()}",
        "previous": None if not current_page.has_previous() else f"?page={current_page.previous_page_number()}",
        "results": list(current_page)
    }

    return JsonResponse({
        "count": 1,
        "next": "1",
        "previous": "",
        "results": [
            {
                "ID": "EE378627348834",
                "FirstName": "John Helmut",
                "LastName": "Smith Carry",
                "BirthCertificateID": "RR-1234567889"
            }
        ]
    }, content_type='application/json')
