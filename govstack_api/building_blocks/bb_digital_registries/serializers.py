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


class InsureeSerializer(serializers.ModelSerializer):
    ID = serializers.CharField(source='id')
    FirstName = serializers.CharField(source='other_names')
    LastName = serializers.CharField(source='last_name')
    BirthCertificateID = serializers.CharField(write_only=True)

    class Meta:
        model = Insuree
        fields = ['ID', 'FirstName', 'LastName', 'BirthCertificateID']
