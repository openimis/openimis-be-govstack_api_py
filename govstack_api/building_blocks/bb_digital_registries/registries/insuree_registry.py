import json

from django.apps import apps
from govstack_api.building_blocks.bb_digital_registries.registries.base_registry import BaseRegistry, RegistryType
from govstack_api.graphql_api_client import GrapheneClient
from insuree.schema import Query, Mutation

config = apps.get_app_config('govstack_api')


class InsureeRegistry(BaseRegistry, RegistryType):
    GQLQuery = Query
    GQLMutation = Mutation