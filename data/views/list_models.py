from django.apps import apps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema


class ListModelsView(APIView):
    """
    API endpoint that provides a list of all available models in the project.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all available models",
        description="Returns a simple key-value pair list of all models available in the project.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "models": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "string"
                        }
                    }
                }
            }
        },
        tags=["System"]
    )
    def get(self, request, *args, **kwargs):
        app_label = request.query_params.get('app_label', None)
        model_name = request.query_params.get('model_name', None)
        
        # Get all models or filter by app_label
        if app_label:
            try:
                app_config = apps.get_app_config(app_label)
                models_list = app_config.get_models()
            except LookupError:
                return Response(
                    {"error": f"App '{app_label}' not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Get all models from all apps
            models_list = []
            for app_config in apps.get_app_configs():
                models_list.extend(app_config.get_models())
        
        # Filter by model name if provided
        if model_name:
            models_list = [m for m in models_list if m.__name__.lower() == model_name.lower()]
            if not models_list:
                return Response(
                    {"error": f"Model '{model_name}' not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Build response data - simple key-value pairs
        result = {}
        for model in models_list:
            # Use model name as key and app_label.model_name as value
            key = model.__name__
            value = f"{model._meta.app_label}.{model.__name__}"
            result[key] = value
        
        return Response({"models": result}, status=status.HTTP_200_OK)
