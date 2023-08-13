from typing import Protocol

import graphene

from govstack_api.building_blocks.bb_digital_registries.registries.registry_qgl_utils import GQLPayloadTemplate, \
    GQLPayloadBuilder, MutationError, RegistryGQLManager


class RegistryType(Protocol):
    def __init__(self, config):
        ...

    def retrieve_filtered_records(
            self, data: dict = None, page: int = None,
            page_size: int = None, ordering=None
    ):
        ...

    def get_record(self, data):
        ...

    def check_record_exists(self, data):
        ...

    def update_multiple_records(self, mapped_data_query: dict = None, mapped_data_write: dict = None) -> int:
        ...

    def create_registry_record(self, mapped_data):
        ...

    def update_registry_record(self, mapped_data_query: dict = None, mapped_data_write: dict = None):
        ...

    def delete_registry_record(self, mapped_data):
        ...

    def create_or_update_registry_record(self, mapped_data_query: dict = None, mapped_data_write: dict = None):
        ...

    def get_record_field(self, record_uuid, field, as_type=None):
        ...


class BaseRegistry:
    @property
    def GQLQuery(self) -> graphene.ObjectType:
        raise NotImplementedError()

    @property
    def GQLMutation(self) -> graphene.ObjectType:
        raise NotImplementedError()

    GQL_PAYLOAD_TEMPLATE = GQLPayloadTemplate()

    def __init__(self, config):
        payload_builder = GQLPayloadBuilder(
            fields_mapping=config['fields_mapping'],
            special_fields=config['special_fields'],
            default_values=config['default_values'],
            id_field=config['id_field']
        )
        self.registry_gql_manager = RegistryGQLManager(
            user=config['user'],
            gql_query=self.GQLQuery,
            gql_mutation=self.GQLMutation,
            payload_builder=payload_builder
        )
        self.model = config['model']
        self.queries = config['queries']
        self.mutations = config['mutations']

    def retrieve_filtered_records(
            self, data: dict = None, page: int = None,
            page_size: int = None, ordering=None
    ):
        return self.registry_gql_manager.retrieve_filtered_records(
            data, self.queries['get'], page, page_size, ordering
        )

    def get_record(self, data):
        return self.registry_gql_manager.get_record(
            data, self.queries['get']
        )

    def check_record_exists(self, data):
        return bool(self.get_record(data))

    def update_multiple_records(self, mapped_data_query: dict = None, mapped_data_write: dict = None) -> int:
        # TODO: This method is unsafe as cannot be made transactional from here. Best
        #  solution would be introduction of bulk update to IMIS mutations.
        records = self.registry_gql_manager.get_record(
            mapped_data_query, self.queries['get'], fetched_fields=['uuid'], only_first=False)
        for record in records:
            mapped_data_write['uuid'] = record['uuid']
            self.registry_gql_manager.mutate_registry_record(self.mutations['update'], mapped_data_write)
        return 200

    def create_registry_record(self, mapped_data):
        self.registry_gql_manager.mutate_registry_record(self.mutations['create'], mapped_data)
        # TODO: This can be misleading if registry was created but entry is not returned then
        #  there will be 404 with content
        return self.registry_gql_manager.get_record(mapped_data, self.queries['get'])

    def update_registry_record(self, mapped_data_query: dict = None, mapped_data_write: dict = None):
        # Internal uuid identifier is required by all update mutations by design
        record = self.registry_gql_manager.get_record(
            mapped_data_query, self.queries['get'], fetched_fields=['uuid'], only_first=False)
        if not record or len(record) == 0:
            raise MutationError("Record not found for provided query.")
        if len(record) > 1:
            raise MutationError("More than one updatable entry found for provided query, aborting.")

        mapped_data_write['uuid'] = record[0]['uuid']
        return self.registry_gql_manager.mutate_registry_record(self.mutations['update'], mapped_data_write)

    def delete_registry_record(self, mapped_data):
        record = self.registry_gql_manager.get_record(
            mapped_data, self.queries['get'], fetched_fields=['uuid'], only_first=False)
        if not record or len(record) == 0:
            raise MutationError("Record not found for provided query.")
        if len(record) > 1:
            raise MutationError("More than one record found for provided query, aborting.")

        delete_data = {'uuids': [record[0]['uuid']]}
        self.registry_gql_manager.mutate_registry_record(self.mutations['delete'], delete_data, False)
        return 204

    def create_or_update_registry_record(self, mapped_data_query: dict = None, mapped_data_write: dict = None):
        # TODO: With numbers of API calls in this method is it quite inefficient
        record = self.registry_gql_manager.get_record(
            mapped_data_query, self.queries['get'], fetched_fields=['uuid'], only_first=False)
        if not record or len(record) == 0:
            return self.create_registry_record(mapped_data_query)
        elif len(record) == 1:
            mapped_data_write['uuid'] = record[0]['uuid']
            self.registry_gql_manager.mutate_registry_record(self.mutations['update'], mapped_data_write)
            return self.registry_gql_manager.get_record(mapped_data_write, self.queries['get'])
        else:
            raise MutationError("More than one updatable entry found for provided query, aborting.")

    def get_record_field(self, record_uuid, field, as_type=None):
        mapped_data = {'uuid': record_uuid}
        record = self.registry_gql_manager.get_record(
            mapped_data, self.queries['get'], fetched_fields=None, only_first=False)

        if not record or len(record) == 0:
            raise MutationError("Record not found for provided query.")
        if len(record) > 1:
            raise MutationError("More than one record found for provided query, aborting.")

        field = record[0][field]
        return as_type(field) if as_type else field
