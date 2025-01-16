
from django.apps import apps
from django.shortcuts import render
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


class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "System Working"})
