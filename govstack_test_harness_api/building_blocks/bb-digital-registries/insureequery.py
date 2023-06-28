import graphene
import datetime
import base64

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from graphene import Schema
from graphene.test import Client
from unittest import mock
from uuid import UUID

from insuree.schema import Query, Mutation
from contribution_plan.tests.helpers import *
# from contribution_plan import schema as contribution_plan_schema


class QueryTest(TestCase):
    class BaseTestContext:
        user = mock.Mock(is_anonymous=False)
        user.has_perm = mock.MagicMock(return_value=False)

    class AnonymousUserContext:
        user = AnonymousUser()

    @staticmethod
    def set_up_env(request):
        client = Client(schema=Schema(query=Query, mutation=Mutation))
        context = QueryTest.BaseTestContext()
        context.user = None
        if request.user.is_authenticated:
            context.user = request.user
        else:
            context = QueryTest.AnonymousUserContext()