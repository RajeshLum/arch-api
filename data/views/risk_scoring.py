from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import *
from ..serializers.risk_scoring import (
    RiskScoringRequestSerializer,
    RiskScoringResponseSerializer,
)
from ..utils.risk_scoring import RiskScorer


class RiskScoringView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Submit Risk Scoring Request",
        description="Calculate risk score for an entity based on provided entity and transaction information.",
        request=inline_serializer(
            name='RiskScoringRequest',
            fields={
                'entity': inline_serializer(
                    name='EntityDetails',
                    fields={
                        'name': serializers.CharField(help_text="Entity name"),
                        'date_of_birth': serializers.DateField(help_text="Date of birth (if individual)"),
                        'nationality': serializers.CharField(help_text="Nationality"),
                        'id_number': serializers.CharField(help_text="Passport, national ID, or company registration number"),
                        'address': serializers.CharField(help_text="Residential or operational address")
                    }
                ),
                'transactions': inline_serializer(
                    name='TransactionDetails',
                    fields={
                        'volume': serializers.FloatField(help_text="Amount of transactions in a specific period"),
                        'frequency': serializers.IntegerField(help_text="Number of transactions in a specific period")
                    }
                )
            }
        ),
        responses={
            200: inline_serializer(
                name='RiskScoringResponse',
                fields={
                    'entity_id': serializers.CharField(),
                    'risk_score': serializers.FloatField(),
                    'risk_category': serializers.CharField(),
                    'reasons': serializers.ListField(child=serializers.CharField()),
                    'breakdown': serializers.DictField(
                        child=serializers.FloatField(),
                        help_text="Detailed breakdown of risk score components"
                    )
                }
            ),
            400: inline_serializer(
                name='ValidationError',
                fields={
                    'errors': serializers.DictField(help_text="Validation errors")
                }
            ),
            422: inline_serializer(
                name='ProcessingError',
                fields={
                    'error': serializers.CharField(),
                    'details': serializers.CharField()
                }
            )
        },
        examples=[
            OpenApiExample(
                'Sample Request',
                value={
                    "entity": {
                        "name": "John Doe",
                        "date_of_birth": "1975-04-21",
                        "nationality": "US",
                        "id_number": "A12345678",
                        "address": "123 Main Street, New York, USA"
                    },
                    "transactions": {
                        "volume": 50000,
                        "frequency": 5
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                'Successful Response',
                value={
                    "entity_id": "1001",
                    "risk_score": 0.87,
                    "risk_category": "High Risk",
                    "reasons": [
                        "High confidence match on OFAC sanctions list.",
                        "Located in high-risk jurisdiction (Country: XYZ).",
                        "Adverse media reports found (e.g., fraud accusations)."
                    ],
                    "breakdown": {
                        "Sanctions Match": 0.4,
                        "PEP": 0.1,
                        "Geography": 0.2,
                        "Adverse Media": 0.15,
                        "Transactions": 0.02
                    }
                },
                response_only=True
            ),
            OpenApiExample(
                'Validation Error',
                value={
                    "errors": {
                        "entity": {
                            "name": ["This field is required."]
                        }
                    }
                },
                status_codes=["400"],
                response_only=True
            )
        ],
        tags=["Risk Assessment"]
    )
    def post(self, request):
        """
        Calculate risk score for an entity based on provided information.
        """
        serializer = RiskScoringRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            risk_scorer = RiskScorer(
                entity_data=serializer.validated_data.get('entity'),
                transaction_data=serializer.validated_data.get('transactions')
            )

            response_data = risk_scorer.generate_response()

            response_serializer = RiskScoringResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)

            return Response(
                response_serializer.validated_data,
                status=status.HTTP_200_OK
            )

        except ValidationError as ve:
            return Response(
                {'error': 'Invalid response data', 'details': ve.detail},
                status=status.HTTP_400_BAD_REQUEST
            )

        except KeyError as ke:
            return Response(
                {'error': 'Invalid data structure', 'details': str(ke)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ValueError as ve:
            return Response(
                {'error': 'Invalid value encountered', 'details': str(ve)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )