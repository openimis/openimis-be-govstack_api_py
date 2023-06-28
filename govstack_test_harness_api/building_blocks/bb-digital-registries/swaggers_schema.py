# swagger_schemas.py
from drf_yasg import openapi

# definition of requests and responses

create_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'write': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_OBJECT, description='Treść do zapisania')
        })
    },
    required=['write']
)

create_response_body = openapi.Response('response description', openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'write': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_OBJECT, description='Treść do zapisania')
        })
    },
    required=['write']
))

content_schema = openapi.Schema(type=openapi.TYPE_OBJECT, ref='#/components/schemas/Example')

query_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'query': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'content': content_schema}, required=['content']),
    },
    required=['query']
)

responses_schema = {
    '200': openapi.Response(
        description='',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'content': content_schema}),
    ),
    '404': openapi.Response(
        description='Record not found',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'detail': openapi.Schema(type=openapi.TYPE_STRING, enum=['no record found'])}),
    ),
}

read_record_schema = {
    'method': 'post',
    'operation_description': 'Searches and returns one record.',
    'request_body': query_schema,
    'responses': responses_schema,
    'security': [{'apiKey': []}],
}


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

content_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={},
    description='Example object'
)

query_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={'content': content_schema},
    required=['content'],
    description='Search object that needs to be updated'
)

write_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={'content': content_schema},
    required=['content'],
    description='Update found object with the following data'
)

request_body_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'query': query_schema,
        'write': write_schema,
    },
    required=['write'],
    description=''
)

update_record_schema = {
    'method': 'put',
    'operation_description': "Updates one existing record in the registry database.",
    'request_body': request_body_schema,
    'responses': {200: openapi.Response(description='')}
}

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
