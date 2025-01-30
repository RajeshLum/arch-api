import operator
from functools import reduce

from django.apps import apps
from django.db.models import Model, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import *


class MatchEntitiesView(APIView):
    def post(self, request, *args, **kwargs):
        queries = request.data.get("queries", {})
        responses = {}

        if not isinstance(queries, dict):
            return Response({"error": "Invalid input format. 'queries' should be a dictionary."}, status=status.HTTP_400_BAD_REQUEST)
        
        for entity_key, entity_data in queries.items():
            schema = entity_data.get("schema")
            properties = entity_data.get("properties", {})

            if not schema or not isinstance(properties, dict):
                responses[entity_key] = {"error": "Invalid schema or properties format."}
                continue

            try:
                model = apps.get_model(app_label="data", model_name=schema)
            except LookupError:
                responses[entity_key] = {"error": f"Model '{schema}' not found in the database."}
                continue

            try:
                filters = []
                for field, values in properties.items():
                    if not isinstance(values, list):
                        responses[entity_key] = {"error": f"Values for field '{field}' must be a list."}
                        break
                    field_queries = Q()
                    for value in values:
                        field_queries |= Q(**{f"{field}__icontains": value})
                    filters.append(field_queries)
                else:
                    results = model.objects.filter(reduce(operator.and_, filters)) if filters else model.objects.all()
                    responses[entity_key] = {
                        "query": entity_data,
                        "results": [
                            {
                                "id": result.id,
                                "attributes": {
                                    field.name: self.serialize_field(getattr(result, field.name))
                                    for field in result._meta.fields
                                },
                            }
                            for result in results
                        ],
                    }
            except Exception as e:
                responses[entity_key] = {"error": f"An error occurred while processing: {str(e)}"}

        return Response({"responses": responses}, status=status.HTTP_200_OK)

    def serialize_field(self, value):
        """
        Convert a field value to a JSON-serializable format.
        """
        try:
            if isinstance(value, Model):
                return str(value)
            elif isinstance(value, (list, dict)):
                return value
            elif hasattr(value, "__dict__"):
                return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
            else:
                return value
        except Exception as e:
            return f"Serialization error: {str(e)}"
