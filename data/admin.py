from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin

# Get all models from the current app
app_models = apps.get_app_config("data").get_models()


# Custom admin class to exclude the 'sanctionEntity' field
class CustomAdmin(ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # Ensure exclude is an iterable and add 'sanctionEntity' if it exists in the model
        self.exclude = list(self.exclude or [])  # Convert None to an empty list
        if hasattr(model, "sanctionEntity"):
            self.exclude.append("sanctionEntity")


# Unregister and re-register all models dynamically
for model in app_models:
    try:
        admin.site.unregister(model)  # Ensure the model is unregistered
    except admin.sites.NotRegistered:
        pass  # Ignore if the model is not registered
    admin.site.register(model, CustomAdmin)


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
