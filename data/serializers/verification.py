from rest_framework import serializers
from data.models import Verification

from django.contrib.auth import get_user_model

class VerificationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        User = get_user_model()
        user_obj = User.objects.filter(id=obj.user_id).first()
        if user_obj:
            return f"{user_obj.first_name} {user_obj.last_name}".strip()
        return None

    class Meta:
        model = Verification
        exclude = []
        read_only_fields = ['user']
