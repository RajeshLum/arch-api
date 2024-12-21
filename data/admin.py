from django.apps import apps
from django.contrib import admin

# Get all models from the current app
app_models = apps.get_app_config("data").get_models()

# Register all models dynamically
for model in app_models:
    admin.site.register(model)
