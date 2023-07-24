from django.http import HttpResponse
from django.conf import settings
from django.apps import apps

from core.schema import Query as core_query, Mutation as core_mutation
from graphene.test import Client
import os
from graphene import Schema
import os
from types import SimpleNamespace
from django.contrib.auth.models import AnonymousUser
from graphene import Schema
from graphene.test import Client
from unittest import mock
from core.schema import Query as CoreQuery, Mutation as CoreMutation
from django.apps import apps


from functools import wraps

def middleware_marker(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request._use_custom_middleware = True
        return view_func(request, *args, **kwargs)
    return _wrapped_view

class InformationMediatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("here 1")
        if getattr(request, '_use_custom_middleware', False):
            print("decorator is true")
            config = apps.get_app_config('govstack_api')
            im_client = config.IM_CLIENT
            im_header = request.META.get('HTTP_INFORMATION_MEDIATOR_CLIENT')
            if im_header != im_client:
                return HttpResponse('Unauthorized', status=401)
            else:
                request.user = self.authenticate_user(request)
                print(request.user)

        return self.get_response(request)

    def get_client(self, schema, query, mutation):
        return Client(schema=schema(query=query, mutation=mutation))

    def create_base_context(self):
        user = mock.Mock(is_anonymous=False)
        user.has_perm = mock.MagicMock(return_value=False)
        return SimpleNamespace(user=user)

    def get_context(self, request):
        if request.user.is_authenticated:
            context = self.create_base_context()
            context.user = request.user
        else:
            context = SimpleNamespace(user=request.user)
        return context

    def authenticate_user(self, request):
        client = self.get_client(Schema, CoreQuery, CoreMutation)
        username = os.getenv('login_openIMIS')
        password = os.getenv('password_openIMIS')

        mutation = f'''
          mutation {{
              tokenAuth(username: "Admin", password: "admin123") {{
                  token
                  refreshExpiresIn
              }}
          }}
          '''
        context = self.get_context(request)
        print(mutation)
        return client.execute(mutation, context=context)


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
