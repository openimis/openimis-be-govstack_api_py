# swagger_schemas.py
from drf_yasg import openapi

# definition of requests and responses

create_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'write': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_OBJECT, description='Content to be saved')
        })
    },
    required=['write']
)

create_response_body = openapi.Response('response description', openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'write': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'content': openapi.Schema(type=openapi.TYPE_OBJECT, description='Content to be saved')
        })
    },
    required=['write']
))

read_value_response_body = openapi.Response('response description', openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'value': openapi.Schema(type=openapi.TYPE_STRING, description='Value of the specified field')
    },
    required=['value']
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

delete_response = openapi.Response(description='No content')

create_or_update_response = {
    200: openapi.Response(
        'Successful update or creation of record',
        openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Updated or newly created object',
                ),
            },
            required=['content'],
        ),
    ),
    400: 'Bad request',
    500: 'Internal server error',
}

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
    description='Search word',
    type=openapi.TYPE_STRING,
)

filter_parameter = openapi.Parameter(
    name='filter',
    in_=openapi.IN_QUERY,
    description='Result filter',
    type=openapi.TYPE_STRING,
)

ordering_parameter = openapi.Parameter(
    name='ordering',
    in_=openapi.IN_QUERY,
    description='Sort type',
    type=openapi.TYPE_STRING,
)

page_parameter = openapi.Parameter(
    name='page',
    in_=openapi.IN_QUERY,
    description='Page number',
    type=openapi.TYPE_INTEGER,
)

page_size_parameter = openapi.Parameter(
    name='page_size',
    in_=openapi.IN_QUERY,
    description='Number of results per page',
    type=openapi.TYPE_INTEGER,
)

query_fieldname_parameter = openapi.Parameter(
    name='query.<fieldname>',
    in_=openapi.IN_QUERY,
    description='Query based on field name',
    type=openapi.TYPE_STRING,
)

get_multiple_records_from_registry_parameters = [
    search_parameter,
    filter_parameter,
    ordering_parameter,
    page_parameter,
    page_size_parameter,
    query_fieldname_parameter,
]

registryname_parameter = openapi.Parameter(
    name='registryname',
    in_=openapi.IN_PATH,
    description='Registry name',
    type=openapi.TYPE_STRING,
)

versionnumber_parameter = openapi.Parameter(
    name='versionnumber',
    in_=openapi.IN_PATH,
    description='Version number',
    type=openapi.TYPE_STRING,
)

uuid_parameter = openapi.Parameter(
    name='uuid',
    in_=openapi.IN_PATH,
    description='Primary key',
    type=openapi.TYPE_STRING,
)

id_parameter = openapi.Parameter(
    name='ID',
    in_=openapi.IN_PATH,
    description='Primary key',
    type=openapi.TYPE_STRING,
)

field_parameter = openapi.Parameter(
    name='field',
    in_=openapi.IN_PATH,
    description='Field name',
    type=openapi.TYPE_STRING,
)

ext_parameter = openapi.Parameter(
    name='ext',
    in_=openapi.IN_PATH,
    description='Data extension',
    type=openapi.TYPE_STRING,
)

read_value_parameters = [
    registryname_parameter,
    versionnumber_parameter,
    uuid_parameter,
    field_parameter,
    ext_parameter,
]

delete_parameters = [
    registryname_parameter,
    versionnumber_parameter,
    id_parameter
]