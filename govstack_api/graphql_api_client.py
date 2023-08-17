from types import SimpleNamespace
from graphene.test import Client
from graphene import Schema


class GrapheneClient:
    def __init__(self, user, query, mutation):
        self._client = Client(Schema(query=query, mutation=mutation))
        self.context = self.get_context(user)

    def get_context(self, user):
        return SimpleNamespace(user=user)

    def execute_query(self, query, variables=None):
        if variables is None:
            variables = {}
        return self._client.execute(query, context=self.context, variables=variables)

    def execute_mutation(self, mutation, variables=None):
        if variables is None:
            variables = {}
        try:
            result = self._client.execute(mutation, context_value=self.context, variables=variables)
            if 'errors' in result:
                raise GraphQLError(result['errors'])
            return result
        except GraphQLError as e:
            print(f"An error occurred during mutation execution: {e}")
            return None


class GraphQLError(Exception):
    """Exception raised for errors in GraphQL queries or mutations."""

    def __init__(self, errors):
        self.errors = errors
        self.message = f"GraphQL errors: {errors}"
        super().__init__(self.message)
