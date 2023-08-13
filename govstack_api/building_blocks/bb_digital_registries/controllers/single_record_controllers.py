from govstack_api.building_blocks.bb_digital_registries.registries.registry_factory import RegistryFactory


def read_single_record_controller(request, validated_data, registryname, versionnumber):
    # do we want to use a specific serializer?
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    registry_record = registry.get_record(validated_data)
    if registry_record:
        return 200, registry_record
    else:
        return 404, {
          "detail": "no record found"  # TODO: Should come from translation
        }


def check_record_presence_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    registry_record = registry.check_record_exists(validated_data)
    if registry_record:
        return 200, registry_record
    else:
        return 404, False


def get_single_record_field_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    registry_record_field = registry\
        .get_record_field(validated_data['uuid'], validated_data['field'], validated_data['ext'])
    
    if registry_record_field:
        return 200, registry_record_field
    else:
        return 404, {}


def update_single_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    update_success = registry.update_registry_record(validated_data['query'], validated_data['write'])
    if update_success:
        return 200, None
    else:
        return 400, {}


def create_single_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    registry_record = registry.create_registry_record(validated_data)
    if registry_record:
        return 200, {'content': registry_record}
    else:
        return 400, {}


def create_or_update_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    registry_record = registry.create_or_update_registry_record(validated_data['query'], validated_data['write'])
    if registry_record:
        return 200, registry_record
    else:
        return 400, {}


def delete_record_controller(request, validated_data, registryname, versionnumber):
    factory = RegistryFactory()
    registry = factory.get_registry(registryname, versionnumber, request.user)
    result = registry.delete_registry_record({'ID': validated_data['ID']})
    if result:
        return 204, {}
    else:
        return 400, {}

