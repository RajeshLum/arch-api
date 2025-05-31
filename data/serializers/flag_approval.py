from rest_framework import serializers
from data.models import FlagApproval

class FlagApprovalSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FlagApproval
        # fields = '__all__'
        exclude = []
        read_only_fields = ['user']
