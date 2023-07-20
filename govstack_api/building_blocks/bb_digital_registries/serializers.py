from rest_framework import serializers

from insuree.models import Insuree


class InsureeSerializer(serializers.ModelSerializer):
    ID = serializers.CharField(source='id')
    FirstName = serializers.CharField(source='other_names')
    LastName = serializers.CharField(source='last_name')
    BirthCertificateID = serializers.CharField(write_only=True)

    class Meta:
        model = Insuree
        fields = ['ID', 'FirstName', 'LastName', 'BirthCertificateID']
