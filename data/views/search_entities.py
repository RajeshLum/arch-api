import operator
from functools import reduce

from django.apps import apps
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import *


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

