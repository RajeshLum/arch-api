from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.models import Organization, Person, SanctionedEntity
from data.utils.risk_scoring_id import RiskScorer


class RiskDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Fetch Risk Score Details",
        description="Get detailed risk assessment information for a specific entity including sanctions, PEP status, geographic risk, and adverse media findings.",
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the entity",
                required=True
            )
        ],
        responses={
            200: inline_serializer(
                name='RiskDetailsResponse',
                fields={
                    'entity_id': serializers.CharField(),
                    'name': serializers.CharField(),
                    'risk_score': serializers.FloatField(),
                    'risk_category': serializers.CharField(),
                    'details': inline_serializer(
                        name='RiskDetails',
                        fields={
                            'sanctions': inline_serializer(
                                name='SanctionsInfo',
                                fields={
                                    'status': serializers.CharField(),
                                    'datasets': serializers.ListField(child=serializers.CharField()),
                                    'confidence': serializers.FloatField()
                                }
                            ),
                            'pep': inline_serializer(
                                name='PepInfo',
                                fields={
                                    'status': serializers.CharField()
                                }
                            ),
                            'geography': inline_serializer(
                                name='GeographyInfo',
                                fields={
                                    'status': serializers.CharField(),
                                    'country': serializers.CharField(),
                                    'reason': serializers.CharField()
                                }
                            ),
                            'adverse_media': inline_serializer(
                                name='AdverseMediaInfo',
                                fields={
                                    'status': serializers.CharField(),
                                    'reports': serializers.ListField(
                                        child=inline_serializer(
                                            name='Report',
                                            fields={
                                                'source': serializers.CharField(),
                                                'details': serializers.CharField()
                                            }
                                        )
                                    )
                                }
                            )
                        }
                    )
                }
            ),
            404: inline_serializer(
                name='NotFoundError',
                fields={
                    'message': serializers.CharField()
                }
            )
        },
        examples=[
            OpenApiExample(
                "Successful Response",
                value={
                    "entity_id": "1001",
                    "name": "John Doe",
                    "risk_score": 0.87,
                    "risk_category": "High Risk",
                    "details": {
                        "sanctions": {
                            "status": "Flagged",
                            "datasets": ["OFAC", "EU"],
                            "confidence": 0.95
                        },
                        "pep": {
                            "status": "Not Flagged"
                        },
                        "geography": {
                            "status": "High Risk",
                            "country": "XYZ",
                            "reason": "Listed as high-risk by FATF."
                        },
                        "adverse_media": {
                            "status": "Flagged",
                            "reports": [
                                {
                                    "source": "News Article",
                                    "details": "Fraud accusation in 2023."
                                }
                            ]
                        }
                    }
                },
                response_only=True
            ),
            OpenApiExample(
                "Entity Not Found",
                value={
                    "message": "Entity not found"
                },
                status_codes=["404"],
                response_only=True
            )
        ],
        tags=["Risk Assessment"]
    )
    def get(self, request, entity_id):
        """
        Fetch detailed risk score information for a specific entity.
        """
        sanctioned_entity = get_object_or_404(SanctionedEntity, sanctionId=entity_id)
        try:
            person = sanctioned_entity.person
            entity_name = person.name[0] if isinstance(person.name, list) else person.name
            nationality = person.country[0] if isinstance(person.country, list) else person.country
        except Person.DoesNotExist:
            try:
                org = sanctioned_entity.organization
                entity_name = org.name[0] if isinstance(org.name, list) else org.name
                nationality = org.country[0] if isinstance(org.country, list) else org.country
            except Organization.DoesNotExist:
                return Response({"message": "Entity is not Person or Organization"})
        
        risk_scorer = RiskScorer(
            entity_id=sanctioned_entity.sanctionId,
            entity_name=entity_name,
            entity_nationality=nationality
        )
        response_data = risk_scorer.generate_response(sanctioned_entity)
            
        return Response(response_data)