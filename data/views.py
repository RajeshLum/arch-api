import operator
from functools import reduce

from django.apps import apps
from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import (
    RiskScoreBreakdownSerializer,
    RiskScoringRequestSerializer,
    RiskScoringResponseSerializer,
)
from .utils import RiskScorer


def dashboard_callback(request, context):
    model_data = []

    app_config = apps.get_app_config('data')  
    models = app_config.get_models()

    for model in models:
        model_name = model.__name__  
        total_records = model.objects.count()  
        model_data.append([model_name, total_records])  

    # Remove 'SanctionedEntity' from model_data if it exists
    model_data = [item for item in model_data if item[0] != 'SanctionedEntity']

    # Sort the model data alphabetically by model name
    model_data.sort(key=lambda x: x[0].lower())  # Sorting by model name (case-insensitive)

    data = {
        "model_data": model_data,  
        "title": "Arch Angel Dashboard",
        # "subtitle": "Model Record Count",
    }

    context.update(data)

    return context

class MatchEntitiesView(APIView):
    def post(self, request, *args, **kwargs):
        queries = request.data.get("queries", {})
        responses = {}

        for entity_key, entity_data in queries.items():
            schema = entity_data.get("schema")
            properties = entity_data.get("properties", {})
            
            try:
                # Dynamically fetch the model based on schema
                model = apps.get_model(app_label="data", model_name=schema)
            except LookupError:
                responses[entity_key] = {
                    "error": f"Model '{schema}' not found in the database."
                }
                continue

            # Build the Q objects for filtering
            filters = []
            for field, values in properties.items():
                field_queries = Q()
                for value in values:
                    field_queries |= Q(**{f"{field}__icontains": value})
                filters.append(field_queries)

            # Perform the query
            results = model.objects.filter(reduce(operator.and_, filters))
            
            # Prepare results with all attributes
            responses[entity_key] = {
                "query": entity_data,
                "results": [
                    {
                        "id": result.id,
                        "score": 0.95,  # Dummy score logic
                        "attributes": {
                            field.name: self.serialize_field(getattr(result, field.name))
                            for field in result._meta.fields
                        }
                    }
                    for result in results
                ]
            }

        return Response({"responses": responses}, status=status.HTTP_200_OK)

    def serialize_field(self, value):
        """
        Convert a field value to a JSON-serializable format.
        """
        if isinstance(value, models.Model):
            # If the field is a related model, return its string representation
            return str(value)
        elif isinstance(value, (list, dict)):
            # Return the value directly if it is already JSON-serializable
            return value
        elif hasattr(value, "__dict__"):
            # For objects with attributes, serialize their dictionary representation
            return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
        else:
            # For other types (e.g., numbers, strings), return the value as is
            return value



class SearchEntitiesView(APIView):
    def get(self, request, *args, **kwargs):
        query_string = request.query_params.get("q", "").strip()
        limit = int(request.query_params.get("limit", 10))
        entity_type = request.query_params.get("entity_type")  # Optional filter
        country = request.query_params.get("country")  # Optional filter
        topics = request.query_params.get("topics")  # Optional filter

        if not query_string:
            return Response(
                {"error": "The 'q' parameter is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        app_config = apps.get_app_config("data")  # Adjust the app name if necessary
        models = app_config.get_models()

        if entity_type:
            # Restrict to a specific model if entity_type is provided
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
                # Create a Q object for wildcard and fuzzy matching
                search_fields = [
                    Q(**{f"{field.name}__icontains": query_string})
                    for field in model._meta.fields
                    if field.get_internal_type() in ["CharField", "TextField"]
                ]
                
                # Apply additional filters if provided
                filters = []
                if country:
                    filters.append(Q(country__icontains=country))
                if topics:
                    filters.append(Q(topics__icontains=topics))

                # Combine all search and filter queries
                combined_query = reduce(operator.or_, search_fields)
                if filters:
                    combined_query &= reduce(operator.and_, filters)

                # Query the model
                query_results = model.objects.filter(combined_query)[:limit]

                # Serialize the results
                for result in query_results:
                    results.append({
                        "id": result.id,
                        "name": str(result),  # Custom `__str__` in the model will be used
                        "relevance": 0.90,  # Placeholder relevance score
                        "attributes": {
                            field.name: self.serialize_field(getattr(result, field.name))
                            for field in result._meta.fields
                        },
                    })

            except Exception as e:
                continue  # Ignore models with issues and proceed to the next one

        # Sort by relevance (placeholder logic)
        results = sorted(results, key=lambda x: x["relevance"], reverse=True)

        return Response({"limit": limit, "results": results[:limit]}, status=status.HTTP_200_OK)

    def serialize_field(self, value):
        """
        Convert a field value to a JSON-serializable format.
        """
        if isinstance(value, models.Model):
            return str(value)  # Serialize related objects as strings
        elif isinstance(value, (list, dict)):
            return value  # JSON-compatible types
        elif hasattr(value, "__dict__"):
            return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
        return value  # Primitive types as-is





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
