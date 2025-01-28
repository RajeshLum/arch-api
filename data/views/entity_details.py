from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import SanctionedEntity
from ..serializers.entity_details import EntityDetailSerializer


class EntityDetailView(APIView):
    """
    API endpoint to fetch detailed information for a specific SanctionedEntity.
    """

    def get(self, request, entity_id):
        try:
            entity = SanctionedEntity.objects.get(sanctionId=entity_id)
        except SanctionedEntity.DoesNotExist:
            raise NotFound(detail="Entity not found.")

        serializer = EntityDetailSerializer(entity)
        return Response(serializer.to_dict(), status=status.HTTP_200_OK)