from rest_framework import serializers


class RecordExistsSerializer(serializers.Serializer):
    query = serializers.JSONField()
    registryname = serializers.CharField(max_length=200)
    versionnumber = serializers.IntegerField()
