import json
from typing import Dict, List

from django.db.models import Q
from fuzzywuzzy import fuzz
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.models import Organization, Person


class ReconcileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_scoring_criteria(self) -> Dict:
        """Define scoring weights for different match criteria."""
        return {
            'name_exact': 100,
            'name_partial': 70,
            'birth_date': 15,
            'nationality': 10,
            'registration_number': 20,
            'address': 10
        }

    def calculate_name_similarity(self, query_name: str, db_names: List[str]) -> float:
        """Calculate the highest similarity score between query name and any DB name."""
        if not db_names:
            return 0.0
            
        scores = [fuzz.ratio(query_name.lower(), db_name.lower()) 
                 for db_name in db_names if db_name]
        return max(scores) / 100 if scores else 0.0

    def reconcile_entity(self, query_data: Dict) -> Dict:
        """Reconcile a single entity against the database."""
        best_match = None
        highest_score = 0
        match_details = {}

        # Get query parameters
        query_name = query_data.get('name', '').strip()
        query_birth_date = query_data.get('birth_date')
        query_nationality = query_data.get('nationality')
        query_reg_number = query_data.get('registration_number')
        query_address = query_data.get('address')

        # Try person matching first
        persons = Person.objects.all()
        
        for person in persons:
            score = 0
            details = {}

            # Name matching (check both name and aliases)
            name_score = self.calculate_name_similarity(
                query_name, 
                [n for n in person.name] if person.name else [] +
                [a for a in person.alias] if person.alias else []
            )
            
            if name_score > 0:
                score += name_score * self.get_scoring_criteria()['name_partial']
                details['name_match'] = name_score

            # Birth date matching
            if query_birth_date and person.birthDate:
                if query_birth_date in person.birthDate:
                    score += self.get_scoring_criteria()['birth_date']
                    details['birth_date_match'] = True

            # Nationality matching
            if query_nationality and person.nationality:
                if query_nationality in person.nationality:
                    score += self.get_scoring_criteria()['nationality']
                    details['nationality_match'] = True

            # Update best match if score is higher
            if score > highest_score:
                highest_score = score
                best_match = person
                match_details = details

        # Normalize final score to 0-1 range
        final_score = min(highest_score / 100, 1.0)

        if best_match:
            return {
                'id': str(best_match.id),
                'name': best_match.name[0] if best_match.name else None,
                'matched_score': round(final_score, 2),
                'match_details': match_details
            }
        
        return None

    def get(self, request):
        """Handle GET request for entity reconciliation."""
        try:
            # Get query data from request
            queries = request.GET.getlist('entities', [])
            if not queries:
                return Response(
                    {"error": "No entities provided for reconciliation."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process each query entity
            results = []
            for query in queries:
                try:
                    query_data = json.loads(query)
                    match_result = self.reconcile_entity(query_data)
                    if match_result:
                        results.append(match_result)
                except json.JSONDecodeError:
                    continue

            return Response({
                "reconciled_entities": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Reconciliation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )