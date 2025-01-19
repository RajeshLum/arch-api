
import operator
from functools import reduce

from django.apps import apps
from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *


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
