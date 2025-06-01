from rest_framework import serializers
from data.amlmodels.aml_services_models import AmlService

class AmlServiceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    service_category_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AmlService
        fields = '__all__'
        read_only_fields = ['user']
    
    def get_service_category_display(self, obj):
        return obj.get_service_category_display()
