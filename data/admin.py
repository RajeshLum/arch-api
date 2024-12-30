from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import Q
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .adminfilters import PersonGenderFilter
from .models import *

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(SanctionedEntity)
class SanctionedEntityModelAdmin(ModelAdmin):
    list_display = (
        # "sanctionId",
        "caption",
        "schema",
        "last_seen",
        "target",
    )
    list_filter = ("target", "schema", "first_seen", "last_seen", "last_change")
    search_fields = ("sanctionId", "caption", "schema")
    ordering = ("-last_seen",)
    date_hierarchy = "last_seen"
    readonly_fields = ("first_seen", "last_seen", "last_change")
    warn_unsaved_form = True
    fieldsets = (
        (
            None,
            {"fields": ("sanctionId", "caption", "schema", "referents", "datasets")},
        ),
        ("Dates", {"fields": ("first_seen", "last_seen", "last_change")}),
        ("Status", {"fields": ("target",)}),
    )


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name",
        "country",
        # "birthDate",
        "gender",
        "nationality",
    )
    list_filter = (
        PersonGenderFilter,
        # "birthCountry",
        # "status",
        # "nationality",
        # "mainCountry",
    )
    search_fields = (
        "sanctionEntity__sanctionId",
        "name",
        "firstName",
        "lastName",
        "email",
        "passportNumber",
    )
    ordering = ("-createdAt",)
    readonly_fields = ("createdAt", "modifiedAt", "sanctionEntity")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "title",
                    "firstName",
                    "lastName",
                    "middleName",
                    "secondName",
                    "nameSuffix",
                    "gender",
                    "birthDate",
                    "birthPlace",
                    "birthCountry",
                    "deathDate",
                )
            },
        ),
        (
            "Personal Details",
            {
                "fields": (
                    "fatherName",
                    "motherName",
                    "ethnicity",
                    "eyeColor",
                    "hairColor",
                    "height",
                    "weight",
                    "appearance",
                    "religion",
                    "political",
                    "education",
                )
            },
        ),
        (
            "Contact Information",
            {"fields": ("email", "phone", "website", "address", "addressEntity")},
        ),
        (
            "Legal and Registration",
            {
                "fields": (
                    "passportNumber",
                    "socialSecurityNumber",
                    "taxNumber",
                    "registrationNumber",
                    "idNumber",
                    "vatCode",
                    "jurisdiction",
                    "mainCountry",
                    "opencorporatesUrl",
                )
            },
        ),
        (
            "Professional Information",
            {"fields": ("position", "sector", "classification", "keywords", "topics")},
        ),
        (
            "Other Identifiers",
            {
                "fields": (
                    "wikidataId",
                    "icijId",
                    "dunsCode",
                    "leiCode",
                    "npiCode",
                    "uniqueEntityId",
                    "swiftBic",
                    "innCode",
                    "ogrnCode",
                    "okpoCode",
                )
            },
        ),
        ("Status and Dates", {"fields": ("status", "createdAt", "modifiedAt")}),
    )

    def get_search_results(self, request, queryset, search_term):
        """Custom search for JSONField."""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            # Add custom filtering for the 'name' JSONField
            json_field_query = Q(name__icontains=search_term)
            queryset |= self.model.objects.filter(json_field_query)
        return queryset, use_distinct
