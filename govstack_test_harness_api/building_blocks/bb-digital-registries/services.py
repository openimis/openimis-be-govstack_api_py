import json
import os

from django.http import HttpResponse
from graphene.test import Client
from graphene import Schema
# from graphqlclient import GraphQLClient
from insuree.schema import Query, Mutation
from .insureequery import *
from core.schema import Query as core_query, Mutation as core_mutation
from insuree.models import Insuree


def get_client(schema, query, mutation):
    return Client(schema=schema(query=query, mutation=mutation))

def get_context(request):
    context = QueryTest.BaseTestContext()
    context.user = None
    print('Request user: ', request.user)
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()
    print('Context user: ', context.user)
    return context


def get_update_registry_query(uuid="", chf_id="", update_fields="") -> str:
    query = f'''
                mutation {{
                  updateInsuree(
                    input: {{
                      clientMutationId: "552f8e55-ed5a-4e1e-a159-ea8f8cec0560"
                      clientMutationLabel: "Update insuree"
                      uuid: "{uuid}"
                      chfId: "{chf_id}"
                {update_fields}
                genderId: "F"
                head: true
                dob: "1974-06-11"
                cardIssued:false
                familyId: 1
                relationshipId: 4
                    }}
                  ) {{
                    clientMutationId
                    internalId
                  }}
                }}
                '''
    return query


def get_insurees_query(variable_values: str = "", fetched_fields: str = "") -> str:
    return f'''
            query GetInsurees {{
                insurees({variable_values}) {{
                    edges{{
                        node{{
                            {fetched_fields}
                        }}
                    }}
                }}
            }}
            '''


def create_insurees_query(variables: dict) -> str:
    return f'''
    mutation {{
        createInsuree(
            input: {{
                clientMutationLabel: "{variables['clientMutationLabel']}"
                chfId: "{variables['chfId']}"
                lastName: "{variables['lastName']}"
                otherNames: "{variables['otherNames']}"
                genderId: "{variables['genderId']}"
                dob: "{variables['dob']}"
                head: {str(variables['head']).lower()}
                cardIssued: {str(variables['cardIssued']).lower()}
                jsonExt: "{variables['jsonExt']}"
                familyId: 1
            }}
        ) {{
            clientMutationId
            internalId
        }}
    }}
    '''

def delete_insuree_query(uuid):
    return f'''mutation
    {{
        deleteInsurees(
            input: {{
            clientMutationId: "c164412c-45a6-4f3f-8a2b-4290739751e2"
            clientMutationLabel: "Delete insuree"

            uuid: "{uuid}", uuids: ["{uuid}"]
        }}
    ) {{
        clientMutationId
    internalId
    }}
    }}
    '''


def get_query_content_values(query_content: dict) -> dict:
    content_values = {}
    if not query_content:
        return {}
    content_values['chfId'] = query_content.get('ID', "")
    content_values['FirstName'] = query_content.get('FirstName', "")
    content_values['LastName'] = query_content.get('LastName', "")
    content_values['BirthCertificateID'] = query_content.get('BirthCertificateID', "")
    return content_values


def get_query_write_values(query_write: dict) -> dict:
    write_values = {}
    if not query_write:
        return {}
    write_values['chfId'] = query_write.get('ID', "")
    write_values['FirstName'] = query_write.get('FirstName', "")
    write_values['LastName'] = query_write.get('LastName', "")
    write_values['BirthCertificateID'] = query_write.get('BirthCertificateID', "")
    return write_values


def get_values_for_insurees(content_values: dict) -> dict:
    return {
        'clientMutationLabel': f"Create insuree - {content_values['chfId']}",
        'chfId': f"{content_values['chfId']}",
        'lastName': f"{content_values['LastName']}",
        'otherNames': f"{content_values['FirstName']}",
        'genderId': 'M',
        'dob': '2000-06-20',
        'head': True,
        'cardIssued': False,
        'jsonExt': '{}',
    }

def get_search_insurees_arguments(query_content: dict) -> str:
    insurees_arguments = ""
    if 'ID' in query_content:
        insurees_arguments += f'chfId: "{query_content["ID"]}",'
    elif 'chfId' in query_content:
        insurees_arguments += f'chfId: "{query_content["chfId"]}",'
    if 'FirstName' in query_content:
        insurees_arguments += f'otherNames: "{query_content["FirstName"]}",'
    if 'LastName' in query_content:
        insurees_arguments += f'lastName: "{query_content["LastName"]}",'
    # if 'BirthCertificateID' in query_content:
    #     variable_values += ": $"

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


# def login(request):
#     client = GraphQLClient('http://localhost:8000/graphql')  # Zastąp to swoim adresem URL
#     mutation = '''
#     mutation {
#         tokenAuth(username: "Admin", password: "admin123") {
#             token
#             refreshExpiresIn
#         }
#     }
#     '''
#     result = client.execute(mutation)
#     result_data = json.loads(result)
#     if 'errors' in result_data:
#         # Obsłuż błędy logowania tutaj
#         pass
#     jwt_token = result_data['data']['tokenAuth']['token']
#     request.session['jwt_token'] = jwt_token  # Zapisz token JWT w sesji
#     return HttpResponse('Logged in.')


def login_with_env_variables(request):
    client = get_client(Schema, core_query, core_mutation)
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
