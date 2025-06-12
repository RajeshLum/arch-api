from rest_framework import serializers
from data.amlmodels.custom_status_models import CustomStatus
from rest_framework import serializers

class CustomStatusSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    value = serializers.CharField(read_only=True)

    class Meta:
        model = CustomStatus
        fields = ['id', 'user', 'label', 'value', 'description', 'created_at', 'updated_at']
        read_only_fields = ['user', 'value', 'created_at', 'updated_at']
