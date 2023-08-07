from rest_framework import serializers


class SingleRecordSerializer(serializers.Serializer):
    registryname = serializers.CharField(max_length=100)
    versionnumber = serializers.CharField(max_length=10)
    uuid = serializers.UUIDField()
    field = serializers.CharField(max_length=50)
    ext = serializers.CharField(max_length=10)

    class Meta:
        fields = ['registryname', 'versionnumber', 'uuid', 'field', 'ext']


class RegistryDeleteSerializer(serializers.Serializer):
    registryname = serializers.CharField(max_length=100)
    versionnumber = serializers.CharField(max_length=10)
    ID = serializers.CharField()

    class Meta:
        fields = ['registryname', 'versionnumber', 'ID']


class MultipleRecordsSerializer(serializers.Serializer):
    registryname = serializers.CharField(max_length=100)
    versionnumber = serializers.CharField(max_length=10)
    search = serializers.CharField(max_length=10)
    filter = serializers.CharField(max_length=10)
    ordering = serializers.CharField(max_length=10)
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    fieldname = serializers.CharField(max_length=50)

    class Meta:
        fields = ['registryname', 'versionnumber', 'search', 'filter', 'ordering', 'page', 'page_size', 'fieldname']


class ContentValidatorSerializer(serializers.Serializer):
    content = serializers.DictField()

    class Meta:
        fields = ['content']


class QueryValidatorSerializer(serializers.Serializer):
    query = ContentValidatorSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret.get('query', {}).get('content', {})

    class Meta:
        fields = ['query']


class AlwaysValidSerializer(serializers.Serializer):
    data = serializers.DictField()

    def is_valid(self, raise_exception=False):
        return True


class WriteValidatorSerializer(serializers.Serializer):
    write = ContentValidatorSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret.get('write', {}).get('content', {})

    class Meta:
        fields = ['write']


class CombinedValidatorSerializer(serializers.Serializer):
    query = ContentValidatorSerializer()
    write = ContentValidatorSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        query_content = ret.get('query', {}).get('content', {})
        write_content = ret.get('write', {}).get('content', {})
        return {'query': query_content, 'write': write_content}

    class Meta:
        fields = ['query', 'write']
