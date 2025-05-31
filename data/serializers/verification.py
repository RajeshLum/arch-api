from rest_framework import serializers
from data.models import Verification

class VerificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Verification
        exclude = []
        read_only_fields = ['user']
