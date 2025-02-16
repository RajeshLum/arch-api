from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import SanctionedEntity
from ..serializers.entity_details import EntityDetailSerializer


class EntityDetailView(APIView):
    """
    API endpoint to fetch detailed information for a specific SanctionedEntity.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='entity_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Unique identifier of the entity (sanctionId).',
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Entity details retrieved successfully.",
                response={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique identifier of the entity."},
                        "name": {"type": "string", "description": "Name of the entity."},
                        "attributes": {
                            "type": "object",
                            "description": "Additional attributes of the entity.",
                            "properties": {
                                "birthDate": {"type": "string", "format": "date", "description": "Birth date of the entity."},
                                "nationality": {"type": "string", "description": "Nationality of the entity."},
                                "address": {"type": "string", "description": "Address of the entity."},
                            },
                        },
                        "linkedEntities": {
                            "type": "array",
                            "description": "List of entities linked to this entity (e.g., family members, subsidiaries).",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "description": "Unique identifier of the linked entity."},
                                    "type": {"type": "string", "description": "Type of the linked entity (e.g., FamilyMember, Subsidiary)."},
                                    "name": {"type": "string", "description": "Name of the linked entity."},
                                },
                            },
                        },
                    },
                },
            ),
            404: OpenApiResponse(
                description="Not Found",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string", "example": "Entity not found."},
                    },
                },
            ),
        },
        examples=[
            OpenApiExample(
                name="Entity Details",
                value={
                    "id": "1001",
                    "name": "John Doe",
                    "attributes": {
                        "birthDate": "1975-04-21",
                        "nationality": "US",
                        "address": "123 Main Street, NY",
                    },
                    "linkedEntities": [
                        {"id": "2001", "type": "FamilyMember", "name": "Jane Doe"},
                    ],
                },
                status_codes=['200'],
            ),
            OpenApiExample(
                name="Entity Not Found",
                value={
                    "detail": "Entity not found.",
                },
                status_codes=['404'],
            ),
        ],
    )
    def get(self, request, entity_id):
        try:
            entity = SanctionedEntity.objects.get(sanctionId=entity_id)
        except SanctionedEntity.DoesNotExist:
            raise NotFound(detail="Entity not found.")

        serializer = EntityDetailSerializer(entity)
        return Response(serializer.to_dict(), status=status.HTTP_200_OK)
    
    