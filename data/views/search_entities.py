import operator
from functools import reduce
from typing import List

from django.apps import apps
from django.db.models import Model, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import *


class SearchEntitiesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Search entities across models",
        description="Performs a case-insensitive search across text fields of entity models. Results are sorted by relevance score.",
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search query string",
                required=True,
                type=str,
                examples=[
                    OpenApiExample(
                        "Example Query",
                        value="example search"
                    ),
                ]
            ),
            OpenApiParameter(
                name="limit",
                description="Maximum number of results to return",
                required=False,
                type=int,
                default=10,
            ),
            OpenApiParameter(
                name="entity_type",
                description="Filter results by specific entity type (model name)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="country",
                description="Filter results by country",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="topics",
                description="Filter results by topics",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "example": 10
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "relevance": {"type": "number"},
                                "attributes": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        }
                    }
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "The 'q' parameter is required."
                    }
                }
            }
        }
    )
    def get(self, request, *args, **kwargs):
        query_string = request.query_params.get("q", "").strip()
        limit = int(request.query_params.get("limit", 10))
        entity_type = request.query_params.get("entity_type") 
        country = request.query_params.get("country") 
        topics = request.query_params.get("topics") 

        if not query_string:
            return Response(
                {"error": "The 'q' parameter is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        app_config = apps.get_app_config("data") 
        models = app_config.get_models()

        if entity_type:
            try:
                models = [apps.get_model(app_label="data", model_name=entity_type)]
            except LookupError:
                return Response(
                    {"error": f"Model '{entity_type}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        results = []

        for model in models:
            try:
                search_fields = [
                    Q(**{f"{field.name}__icontains": query_string})
                    for field in model._meta.fields
                    if field.get_internal_type() in ["CharField", "TextField"]
                ]
                
                filters = []
                if country:
                    filters.append(Q(country__icontains=country))
                if topics:
                    filters.append(Q(topics__icontains=topics))

                combined_query = reduce(operator.or_, search_fields)
                if filters:
                    combined_query &= reduce(operator.and_, filters)

                query_results = model.objects.filter(combined_query)[:limit]

                for result in query_results:
                    relevance_score = self.calculate_relevance(query_string, result)
                    results.append({
                        "id": result.id,
                        "name": str(result),
                        "relevance": relevance_score,
                        "attributes": {
                            field.name: self.serialize_field(getattr(result, field.name))
                            for field in result._meta.fields
                        },
                    })

            except Exception as e:
                continue  

        results = sorted(results, key=lambda x: x["relevance"], reverse=True)

        return Response({"limit": limit, "results": results[:limit]}, status=status.HTTP_200_OK)

    def calculate_relevance(self, query, result):
        """
        Calculate relevance based on how well the result matches the query.
        """
        match_count = sum(
            1 for field in result._meta.fields 
            if field.get_internal_type() in ["CharField", "TextField"] and 
               query.lower() in str(getattr(result, field.name)).lower()
        )
        total_fields = sum(
            1 for field in result._meta.fields if field.get_internal_type() in ["CharField", "TextField"]
        )
        return round(match_count / total_fields, 2) if total_fields else 0.0

    def serialize_field(self, value):
        try:
            if isinstance(value, Model):
                return str(value)
            elif isinstance(value, (list, dict)):
                return value
            elif hasattr(value, "__dict__"):
                return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
            return value
        except Exception as e:
            return f"Serialization error: {str(e)}"