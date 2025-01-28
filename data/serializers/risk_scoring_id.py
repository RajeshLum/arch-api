from rest_framework import serializers


class SanctionsDetailSerializer(serializers.Serializer):
    status = serializers.CharField()
    datasets = serializers.ListField(child=serializers.CharField(), required=False)
    confidence = serializers.FloatField(required=False)

class PEPDetailSerializer(serializers.Serializer):
    status = serializers.CharField()

class GeographyDetailSerializer(serializers.Serializer):
    status = serializers.CharField()
    country = serializers.CharField(required=False)
    reason = serializers.CharField(required=False)

class AdverseMediaReportSerializer(serializers.Serializer):
    source = serializers.CharField()
    details = serializers.CharField()

class AdverseMediaDetailSerializer(serializers.Serializer):
    status = serializers.CharField()
    reports = AdverseMediaReportSerializer(many=True, required=False)

class RiskDetailsResponseSerializer(serializers.Serializer):
    entity_id = serializers.CharField()
    name = serializers.CharField()
    risk_score = serializers.FloatField()
    risk_category = serializers.CharField()
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        return {
            'sanctions': obj.get('sanctions', {}),
            'pep': obj.get('pep', {}),
            'geography': obj.get('geography', {}),
            'adverse_media': obj.get('adverse_media', {})
        }
