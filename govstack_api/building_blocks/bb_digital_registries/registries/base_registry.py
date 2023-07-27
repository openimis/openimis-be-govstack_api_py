from abc import ABC, abstractmethod


class BaseRegistry:
    def get_record(self):
        pass

    def update_record(self):
        pass

    def delete_record(self):
        pass

    def check_if_record_exists(self):
        pass

class Registry(ABC):
    def __init__(self, request, config):
        self.fields_mapping = config['fields_mapping']
        self.special_fields = config['special_fields']
        self.default_values = config['default_values']
        self.mutations = config['mutations']

    @abstractmethod
    def create_record(self, data):
        pass

    @abstractmethod
    def update_record(self, data):
        pass