import json

from django.apps import apps
from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import BaseRegistry, RegistryType
from govstack_api.graphql_api_client import GrapheneClient
from insuree.schema import Query, Mutation
from insuree.models import InsureeMutation
config = apps.get_app_config('govstack_api')


class InsureeRegistry(BaseRegistry, RegistryType):
    GQLQuery = Query
    GQLMutation = Mutation

    def get_id_by_mutation_key(self, mutation_id, id_field):
        mutation = InsureeMutation.objects.get(mutation_id=mutation_id)
        return mutation.insuee.get(id_field)
