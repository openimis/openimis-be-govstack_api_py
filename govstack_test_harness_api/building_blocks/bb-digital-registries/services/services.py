import os
from types import SimpleNamespace
from django.contrib.auth.models import AnonymousUser
from graphene import Schema
from graphene.test import Client
from unittest import mock
from core.schema import Query as CoreQuery, Mutation as CoreMutation
from django.apps import apps

app_config = apps.get_app_config('govstack_test_harness_api')


def get_client(schema, query, mutation):
    return Client(schema=schema(query=query, mutation=mutation))


def create_base_context():
    user = mock.Mock(is_anonymous=False)
    user.has_perm = mock.MagicMock(return_value=False)
    return SimpleNamespace(user=user)


def get_context(request):
    if request.user.is_authenticated:
        context = create_base_context()
        context.user = request.user
    else:
        context = SimpleNamespace(user=request.user)
    return context


def get_query_content_values(query_content: dict, registry_name: str, version: str) -> dict:
    content_values = {}
    if not query_content:
        return {}

    json_mapping = app_config.digital_registry.get(registry_name, {}).get(version, {})
    for input_key, output_key in json_mapping.items():
        content_values[output_key] = query_content.get(input_key, "")
    return content_values


def get_values_for_insurees(content_values: dict, registry_name: str, version: str) -> dict:
    json_mapping = app_config.digital_registry.get(registry_name, {}).get(version, {})
    mapped_values = {json_mapping[key]: value for key, value in content_values.items() if key in json_mapping}
    return {
        'clientMutationLabel': f"Create insuree - {mapped_values.get('chfId', '')}",
        'chfId': f"{mapped_values.get('chfId', '')}",
        'lastName': f"{mapped_values.get('lastName', '')}",
        'otherNames': f"{mapped_values.get('otherNames', '')}",
        'genderId': mapped_values.get('Gender', 'M'),
        'dob': mapped_values.get('BirthDate', '2000-06-20'),
        'head': mapped_values.get('Head', True),
        'cardIssued': False,
        'jsonExt': '{}',
    }


def get_search_insurees_arguments(query_content: dict, registry_name: str, version: str) -> str:
    insurees_arguments = ""
    json_mapping = app_config.digital_registry.get(registry_name, {}).get(str(version), {})
    for key, value in json_mapping.items():
        if key in query_content:
            insurees_arguments += f'{value}: "{query_content[key]}",'

    if insurees_arguments.endswith(','):
        return insurees_arguments[:-1]
    return insurees_arguments


def get_update_fields(write_values) -> str:
    field_mapping = {
        "LastName": "lastName",
        "FirstName": "otherNames"
    }
    return "".join(f'{field_mapping[key]}: "{value}" '
                            for key, value in write_values.items()
                            if value and key in field_mapping)


def login_with_env_variables(request):
    client = get_client(Schema, CoreQuery, CoreMutation)
    username = os.getenv('login_openIMIS')
    password = os.getenv('password_openIMIS')

    mutation = f'''
      mutation {{
          tokenAuth(username: "{username}", password: "{password}") {{
              token
              refreshExpiresIn
          }}
      }}
      '''
    context = get_context(request)
    client.execute(mutation, context=context)
    return context
