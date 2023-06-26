# swagger_schemas.py
from drf_yasg import openapi

# definition of requests and responses

create_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'write': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='Treść do zapisania')
        })
    },
    required=['write']
)

create_response_body = openapi.Response('response description', openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'write': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='Treść do zapisania')
        })
    },
    required=['write']
))


exists_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'query': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_OBJECT, description='Search content')
        }),
    },
    required=['query']
)

exists_response_body = openapi.Response('response description', openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'answer': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Example object found in database'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='More information about the object')
        })
    },
    required=['answer']
))


# Parameters

search_parameter = openapi.Parameter(
    name='search',
    in_=openapi.IN_QUERY,
    description='Wyszukiwane słowo',
    type=openapi.TYPE_STRING,
)

filter_parameter = openapi.Parameter(
    name='filter',
    in_=openapi.IN_QUERY,
    description='Filtr wyników',
    type=openapi.TYPE_STRING,
)

ordering_parameter = openapi.Parameter(
    name='ordering',
    in_=openapi.IN_QUERY,
    description='Sposób sortowania wyników',
    type=openapi.TYPE_STRING,
)

page_parameter = openapi.Parameter(
    name='page',
    in_=openapi.IN_QUERY,
    description='Numer strony',
    type=openapi.TYPE_INTEGER,
)

page_size_parameter = openapi.Parameter(
    name='page_size',
    in_=openapi.IN_QUERY,
    description='Ilość wyników na stronę',
    type=openapi.TYPE_INTEGER,
)

query_fieldname_parameter = openapi.Parameter(
    name='query.<fieldname>',
    in_=openapi.IN_QUERY,
    description='Zapytanie w oparciu o nazwę pola',
    type=openapi.TYPE_STRING,
)

# Zbiorcza lista wszystkich parametrów

get_multiple_records_from_registry_parameters = [
    search_parameter,
    filter_parameter,
    ordering_parameter,
    page_parameter,
    page_size_parameter,
    query_fieldname_parameter,
]
