from types import SimpleNamespace
from unittest import mock
from graphene.test import Client
from graphene import Schema


class GrapheneClient:
    def __init__(self, request, query, mutation):
        self._client = Client(Schema(query=query, mutation=mutation))
        self.context = self.get_context(request)

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

    def execute_query(self, query,variables=None):
        print("context: ", self.context)

        if variables is None:
            variables = {}
        print("variables: ", variables)
        return self._client.execute(query, context=self.context, variables=variables)

    def execute_mutation(self, mutation, variables=None):
        if variables is None:
            variables = {}

        return self._client.execute(mutation, context_value=self.context, variables=variables)
