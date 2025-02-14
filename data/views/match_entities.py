import operator
from functools import reduce
from typing import Any, Dict, List

from django.apps import apps
from django.db.models import Model, Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import *


def generate_models_docs():
    """Generate documentation for all models outside the class"""
    app_config = apps.get_app_config("data")
    models_info = {}
    
    for model in app_config.get_models():
        model_name = model._meta.model_name
        models_info[model_name] = {
            "fields": {
                field.name: {
                    "type": field.get_internal_type(),
                    "help_text": field.help_text,
                    "nullable": field.null,
                }
                for field in model._meta.fields
            }
        }

    return "\n\n".join(
        f"- {model_name}:\n" + "\n".join(
            f"  - {field_name}: {info['type']}" + 
            (f" ({info['help_text']})" if info['help_text'] else "") +
            (" (nullable)" if info['nullable'] else "")
            for field_name, info in fields["fields"].items()
        )
        for model_name, fields in models_info.items()
    )


def generate_example_request():
    """Generate example request outside the class"""
    app_config = apps.get_app_config("data")
    example_request = {"queries": {}}
    
    for model in app_config.get_models():
        model_name = model._meta.model_name
        example_request["queries"][model_name] = {
            "schema": model_name,
            "properties": {}
        }
        
        for field in model._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                example_request["queries"][model_name]["properties"][field.name] = [
                    f"example_{field.name}",
                    f"another_{field.name}"
                ]
            elif isinstance(field, models.IntegerField):
                example_request["queries"][model_name]["properties"][field.name] = ["1", "2"]
            elif isinstance(field, models.DateTimeField):
                example_request["queries"][model_name]["properties"][field.name] = [
                    "2024-02-14T12:00:00Z"
                ]
    
    return example_request


class MatchEntitiesView(APIView):
    """API to match the entities to database entity"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Match entities against database records",
        description="""
        Match provided entities against database records using flexible property matching.
        For each entity query, specify:
        - schema: The model/entity type to search against
        - properties: Dictionary of field names and their possible values to match
        
        Available Models and Their Fields:
        {models_docs}
        """.format(models_docs=generate_models_docs()),
        request=inline_serializer(
            name='MatchEntitiesRequest',
            fields={
                'queries': serializers.DictField(
                    child=serializers.DictField(
                        child=serializers.JSONField(),
                        allow_empty=False
                    ),
                    help_text="Dictionary of entity queries to process"
                )
            }
        ),
        responses={
            200: inline_serializer(
                name='MatchEntitiesResponse',
                fields={
                    'responses': serializers.DictField(
                        child=serializers.DictField(
                            child=serializers.JSONField()
                        ),
                        help_text="Dictionary of matching results for each query"
                    )
                }
            ),
            400: inline_serializer(
                name='MatchEntitiesError',
                fields={
                    'error': serializers.CharField()
                }
            )
        },
        examples=[
            OpenApiExample(
                'Valid Request with Dynamic Fields',
                description='Example request showing how to query different models',
                value=generate_example_request(),
                request_only=True
            ),
            OpenApiExample(
                'Successful Response',
                value={
                    "responses": {
                        "example_entity": {
                            "query": {
                                "schema": "ExampleModel",
                                "properties": {
                                    "name": ["test"],
                                    "description": ["example"]
                                }
                            },
                            "results": [
                                {
                                    "id": 1,
                                    "attributes": {
                                        "id": 1,
                                        "name": "Test Entity",
                                        "description": "Example Description",
                                        "created_at": "2024-02-14T12:00:00Z"
                                    }
                                }
                            ]
                        }
                    }
                },
                response_only=True
            )
        ]
    )
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
        """Convert a field value to a JSON-serializable format."""
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