from rest_framework import serializers

from insuree.models import Insuree
from rest_framework import serializers


class QueryContentValidatorSerializer(serializers.Serializer):
    content = serializers.DictField()

    class Meta:
        fields = ['content']


class QueryValidatorSerializer(serializers.Serializer):
    query = QueryContentValidatorSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret.get('query', {}).get('content', {})

    class Meta:
        fields = ['query']


class SingleRecordSerializer(serializers.Serializer):
    registryname = serializers.CharField(max_length=100)
    versionnumber = serializers.CharField(max_length=10)
    uuid = serializers.UUIDField()
    field = serializers.CharField(max_length=50)
    ext = serializers.CharField(max_length=10)
