from django.db.models import Q
from graphene.test import Client
from graphene import Schema
from insuree.schema import Query, Mutation
from .insureequery import *
from insuree.models import Insuree


def check_if_registry_exists(registryname, versionnumber, query_content) -> bool:

    # if not possible to check registry then pass

    filters = []
    if 'ID' in query_content:
        filters.append(Q(id=query_content['ID']))
    if 'FirstName' in query_content:
        filters.append(Q(other_names=query_content['FirstName']))
    if 'LastName' in query_content:
        filters.append(Q(last_name=query_content['LastName']))
    if 'BirthCertificateID' in query_content:
        filters.append(Q(json_ext=query_content['BirthCertificateID']))

    insuree_exists = Insuree.objects.filter(*filters).exists()

    return insuree_exists


def get_client(schema, query, mutation):
    return Client(schema=schema(query=query, mutation=mutation))

def get_context(request):
    context = QueryTest.BaseTestContext()
    context.user = None
    if request.user.is_authenticated:
        context.user = request.user
    else:
        context = QueryTest.AnonymousUserContext()
    return context
