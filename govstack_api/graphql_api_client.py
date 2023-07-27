from types import SimpleNamespace
from unittest import mock
from graphene.test import Client
from graphene import Schema


class GrapheneClient:
    def __init__(self, request, query, mutation):
        self._client = Client(Schema(query=query, mutation=mutation))
        self.context = self.get_context(request)

    def get_context(self, request):
        return SimpleNamespace(user=request.user)

    def execute_query(self, query,variables=None):
        if variables is None:
            variables = {}
        return self._client.execute(query, context=self.context, variables=variables)

    def execute_mutation(self, mutation, variables=None):
        if variables is None:
            variables = {}

        return self._client.execute(mutation, context_value=self.context, variables=variables)
