from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import *
from ..serializers.risk_scoring import (
    RiskScoreBreakdownSerializer,
    RiskScoringRequestSerializer,
    RiskScoringResponseSerializer,
)
from ..utils.risk_scoring import RiskScorer


class RiskScoringView(APIView):
    # permission_classes = [IsAuthenticated]
    
    # @extend_schema(
    #     request=RiskScoringRequestSerializer,
    #     responses={200: RiskScoringResponseSerializer},
    #     description="Calculate AML risk score for an entity",
    #     summary="Generate AML Risk Score"
    # )
    def post(self, request):
        """
        Calculate risk score for an entity based on provided information.
        """
        serializer = RiskScoringRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
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
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
