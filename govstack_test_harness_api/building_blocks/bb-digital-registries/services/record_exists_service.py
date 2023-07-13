# W pliku record_exists_service.py
from graphene import Schema

from ..gql.graphene_client import GrapheneClient
from ..gql.gql_queries import get_record_exists_query, get_insurees_query
from .services import get_client, get_values_for_insurees, get_search_insurees_arguments
from insuree.schema import Query, Mutation
from django.conf import global_settings


class RecordExistsService:
    def __init__(self, jwt_token, context, validated_data):
        self.context = context
        self.validated_data = validated_data
        # self.headers = {"Authorization": "Bearer " + jwt_token}
        self.client = GrapheneClient()

    def execute(self):
        variables = get_values_for_insurees(
            self.validated_data['query']['content'],
            self.validated_data["registryname"],
            self.validated_data["versionnumber"]
        )
        variable_values = get_search_insurees_arguments(
            self.validated_data['query']['content'],
            self.validated_data["registryname"],
            self.validated_data["versionnumber"]
        )
        query = get_insurees_query(variable_values, "lastName")
        return self.client.execute_query(query, self.context, variables)
