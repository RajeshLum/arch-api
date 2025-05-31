from rest_framework import serializers
from data.models import ResearchRequest

class ResearchRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ResearchRequest
        # fields = '__all__'
        exclude = []
        read_only_fields = ['user']
