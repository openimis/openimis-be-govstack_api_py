import graphene
from graphene.test import Client
# from gql import gql, Client
# from gql.transport.requests import RequestsHTTPTransport
from insuree.schema import Query, Mutation
from graphene import Schema


class GrapheneClient:
    def __init__(self):
        self._client = Client(Schema(query=Query, mutation=Mutation))

    def execute_query(self, query, context, variables=None):
        print("context: ", context)

        if variables is None:
            variables = {}
        print("variables: ", variables)
        return self._client.execute(query, context=context, variables=variables)

    def execute_mutation(self, mutation, variables=None):
        if variables is None:
            variables = {}

        return self._client.execute(mutation, variables=variables)


# class GrapheneClient:
#     def __init__(self, url, headers=None):
#         if headers is None:
#             headers = {}
#         print(url)
#         self._transport = RequestsHTTPTransport(url=url, headers=headers, use_json=True)
#         self._client = Client(transport=self._transport, fetch_schema_from_transport=True)
#
#     def execute_query(self, query, variables=None):
#         if variables is None:
#             variables = {}
#
#         return self._client.execute(gql(query), variable_values=variables)
#
#     def execute_mutation(self, mutation, variables=None):
#         if variables is None:
#             variables = {}
#
#         return self._client.execute(gql(mutation), variable_values=variables)
