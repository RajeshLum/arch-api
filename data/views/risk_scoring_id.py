from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import Organization, Person, SanctionedEntity
from data.utils.risk_scoring_id import RiskScorer


class RiskDetailsView(APIView):
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
