from django.http import HttpResponse
import os
from types import SimpleNamespace
from graphene import Schema
from graphene.test import Client
from unittest import mock
from core.schema import Query as CoreQuery, Mutation as CoreMutation
from django.apps import apps
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from functools import wraps


def authenticate_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        config = apps.get_app_config('govstack_api')
        im_client = config.IM_CLIENT
        im_header = request.META.get('HTTP_INFORMATION_MEDIATOR_CLIENT')
        if im_header != im_client:
            return HttpResponse('Unauthorized', status=401)
        else:
            # self.authenticate_user(request)
            pass

        return view_func(request, *args, **kwargs)
    return _wrapped_view


class InformationMediatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.headers.get('Information-Mediator-Client', None):
            config = apps.get_app_config('govstack_api')
            im_client = config.IM_CLIENT
            im_header = request.META.get('HTTP_INFORMATION_MEDIATOR_CLIENT')
            if im_header != im_client:
                return HttpResponse('Unauthorized', status=401)
            else:
                self.authenticate_user(request)
        response = self.get_response(request)
        return response

    def get_client(self, schema, query, mutation):
        return Client(schema=schema(query=query, mutation=mutation))

    def create_base_context(self):
        user = mock.Mock(is_anonymous=False)
        user.has_perm = mock.MagicMock(return_value=False)
        return SimpleNamespace(user=user)

    def get_context(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            context = self.create_base_context()
            context.user = request.user
        else:
            context = SimpleNamespace(user=None)
        return context

    def authenticate_user(self, request):
        client = self.get_client(Schema, CoreQuery, CoreMutation)
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
        context = self.get_context(request)
        result = client.execute(mutation, context=context)
        return result


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


#@database_sync_to_async
def get_user(token):
    User = get_user_model()
    try:
        user = User.objects.get(auth_token=token)
        return user
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name.lower() == 'bearer':
                scope['user'] = await get_user(token_key)
        return await super().__call__(scope, receive, send)
