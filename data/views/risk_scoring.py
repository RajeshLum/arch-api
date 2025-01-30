from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import *
from ..serializers.risk_scoring import (
    RiskScoringRequestSerializer,
    RiskScoringResponseSerializer,
)
from ..utils.risk_scoring import RiskScorer


class RiskScoringView(APIView):
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

        # except Exception as e:
        #     print(e)
        #     return Response(
        #         {'error': 'Internal server error', 'details': 'An unexpected error occurred.'},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
