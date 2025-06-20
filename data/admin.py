from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .filters.adminfilters import PersonGenderFilter
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
        "sanctionId",
        
        "caption",
        "get_related_model_link",
        "target",
        "last_seen",
    )
    list_filter = ("target", "schema", "first_seen", "last_seen", "last_change")
    search_fields = ("sanctionId", "caption", "schema")
    ordering = ("-last_seen",)
    date_hierarchy = "last_seen"
    readonly_fields = ("first_seen", "schema", "last_seen", "last_change")
    warn_unsaved_form = True
    fieldsets = (
        (
            None,
            {"fields": ("sanctionId", "caption", "schema", "referents", "datasets")},
        ),
        ("Dates", {"fields": ("first_seen", "last_seen", "last_change")}),
        ("Status", {"fields": ("target",)}),
    )

    @admin.display(description="Data Schema")
    def get_related_model_link(self, obj):
        """
        Generate a link to the related model's admin change page based on the `schema` field value.
        """
        # Get the schema value from the SanctionedEntity instance
        schema_value = obj.schema

        if schema_value:
            try:
                # Dynamically fetch the model class using schema_value
                model_class = apps.get_model("data", schema_value.capitalize())

                # Get the related instance using the reverse relationship
                related_instance = model_class.objects.get(sanctionEntity=obj)

                # Generate the admin change URL for the related instance
                url = reverse(
                    f"admin:{model_class._meta.app_label}_{model_class._meta.model_name}_change",
                    args=[related_instance.pk],
                )
                return format_html(
                    '<a href="{}" style="text-style:underline !important">{}</a>',
                    url,
                    model_class._meta.verbose_name.capitalize(),
                )
            except (AttributeError, model_class.DoesNotExist):
                return "No related instance"

        return "No matching schema"


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",
        "gender_display",
        "nationality_display",
    )
    list_filter = (PersonGenderFilter,)
    search_fields = (
        "sanctionEntity__sanctionId",
        "name",
        "firstName",
        "lastName",
        "email",
        "country",
        "nationality",
        "passportNumber",
        "gender",
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


       
    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"
    
    def gender_display(self, obj):
        """Custom display for the 'gender' field."""
        if isinstance(obj.gender, list) and len(obj.gender) == 1:
            return obj.gender[0]
        return obj.gender

    gender_display.short_description = "Gender"
    
    def country_display(self, obj):
        """Custom display for the 'country' field."""
        if isinstance(obj.country, list) and len(obj.country) == 1:
            return obj.country[0]
        return obj.country

    country_display.short_description = "Country"
    
    def nationality_display(self, obj):
        """Custom display for the 'nationality' field."""
        if isinstance(obj.nationality, list) and len(obj.nationality) == 1:
            return obj.nationality[0]
        return obj.nationality

    nationality_display.short_description = "Nationality"


@admin.register(Sanction)
class SanctionAdmin(ModelAdmin):
    list_display = ("sanctionEntity", "entity_display", "country_display")
    search_fields = (
        "entity",
        "recordId",
        "sourceUrl",
        "authority",
        "unscId",
        "program",
        "country"
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Dates and Status",
            {"fields": ("startDate", "endDate", "date", "status", "listingDate")},
        ),
        (
            "Details",
            {
                "fields": (
                    "entity",
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                    "authority",
                    "authorityId",
                    "unscId",
                    "program",
                    "programId",
                    "programUrl",
                    "provisions",
                    "duration",
                    "reason",
                    "country",
                )
            },
        ),
        ("Audit", {"fields": ("modifiedAt",)}),
    )
    
       
    def entity_display(self, obj):
        """Custom display for the 'entity' field."""
        if isinstance(obj.entity, list) and len(obj.entity) == 1:
            return obj.entity[0]
        return obj.entity

    entity_display.short_description = "Entity"

    def country_display(self, obj):
        """Custom display for the 'country' field."""
        if isinstance(obj.country, list) and len(obj.country) == 1:
            return obj.country[0]
        return obj.country

    country_display.short_description = "Country"



@admin.register(Family)
class FamilyAdmin(ModelAdmin):
    list_display = ("person_display", "relationship_display", "relative_display")
    search_fields = ("person", "relative", "relationship", "summary", "recordId")
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Dates",
            {"fields": ("startDate", "endDate", "date")},
        ),
        (
            "Relationship Details",
            {"fields": ("person", "relative", "relationship")},
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        ("Audit", {"fields": ("modifiedAt",)}),
    )
    
    
    def person_display(self, obj):
        """Custom display for the 'person' field."""
        if isinstance(obj.person, list) and len(obj.person) == 1:
            return obj.person[0]
        return obj.person

    person_display.short_description = "Person"
    
    def relative_display(self, obj):
        """Custom display for the 'relative' field."""
        if isinstance(obj.relative, list) and len(obj.relative) == 1:
            return obj.relative[0]
        return obj.relative

    relative_display.short_description = "Relative"
    
    def relationship_display(self, obj):
        """Custom display for the 'relationship' field."""
        if isinstance(obj.relationship, list) and len(obj.relationship) == 1:
            return obj.relationship[0]
        return obj.relationship

    relationship_display.short_description = "Relationship"


@admin.register(CryptoWallet)
class CryptoWalletAdmin(ModelAdmin):
    list_display = ("sanctionEntity", "currency_name", "holder_name")
    search_fields = (
        "name",
        "alias",
        "previousName",
        "sourceUrl",
        "address", 
        "publicKey",
        "currency",
        "holder",
    )
    ordering = ("-createdAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "address",
                    "addressEntity",
                )
            },
        ),
        (
            "Financial Details",
            {
                "fields": (
                    "amount",
                    "currency",
                    "amountUsd",
                    "balance",
                    "mangingExchange",
                    "holder",
                )
            },
        ),
        (
            "Technical Details",
            {
                "fields": (
                    "publicKey",
                    "program",
                    "notes",
                    "wikidataId",
                    "keywords",
                    "topics",
                )
            },
        ),
        (
            "References",
            {"fields": ("sourceUrl", "publisher")},
        ),
        ("Audit", {"fields": ("createdAt", "modifiedAt")}),
    )
    
    def currency_name(self, obj):
        """Custom display for the 'currency' field."""
        if isinstance(obj.currency, list) and len(obj.currency) == 1:
            return obj.currency[0]
        return obj.currency
    
    def holder_name(self, obj):
        """Custom display for the 'holder' field."""
        if isinstance(obj.holder, list) and len(obj.holder) == 1:
            return obj.holder[0]
        return obj.holder


@admin.register(Succession)
class SuccessionAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "predecessor_display",
        "successor_display",
        "role",
        "status",
    )
    search_fields = (
        "predecessor",
        "successor",
        "role",
        "status",
        "summary",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Dates and Status",
            {"fields": ("startDate", "endDate", "date", "status")},
        ),
        (
            "Succession Details",
            {
                "fields": (
                    "predecessor",
                    "successor",
                    "role",
                    "summary",
                    "description",
                    "recordId",
                )
            },
        ),
        (
            "References",
            {"fields": ("sourceUrl", "publisher")},
        ),
        ("Audit", {"fields": ("modifiedAt",)}),
    )

    def predecessor_display(self, obj):
        """Custom display for the 'predecessor' field."""
        if isinstance(obj.predecessor, list) and len(obj.predecessor) == 1:
            return obj.predecessor[0]
        return obj.predecessor

    predecessor_display.short_description = "Predecessor"

    def successor_display(self, obj):
        """Custom display for the 'successor' field."""
        if isinstance(obj.successor, list) and len(obj.successor) == 1:
            return obj.successor[0]
        return obj.successor

    successor_display.short_description = "Successor"


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",
        "status_display",
        "sector_display",
    )
    search_fields = (
        "name",
        "email",
        "phone",
        "website",
        "registrationNumber",
        "taxNumber",
        "country",
        "status",
        "sector",
    )
    ordering = ("-modifiedAt",)
    # list_filter = ["sector"]
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    # fieldsets = (
    #     ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
    #     (
    #         "Company Details",
    #         {
    #             "fields": (
    #                 "name",
    #                 "summary",
    #                 "description",
    #                 "alias",
    #                 "previousName",
    #                 "weakAlias",
    #                 "status",
    #                 "sector",
    #                 "classification",
    #                 "parent",
    #             )
    #         },
    #     ),
    #     (
    #         "Legal Information",
    #         {
    #             "fields": (
    #                 "registrationNumber",
    #                 "idNumber",
    #                 "taxNumber",
    #                 "vatCode",
    #                 "jurisdiction",
    #                 "mainCountry",
    #                 "opencorporatesUrl",
    #             )
    #         },
    #     ),
    #     (
    #         "Corporate Identifiers",
    #         {
    #             "fields": (
    #                 "icijId",
    #                 "okpoCode",
    #                 "innCode",
    #                 "ogrnCode",
    #                 "leiCode",
    #                 "dunsCode",
    #                 "uniqueEntityId",
    #                 "npiCode",
    #                 "swiftBic",
    #                 "cageCode",
    #                 "permId",
    #                 "imoNumber",
    #                 "giiNumber",
    #             )
    #         },
    #     ),
    #     (
    #         "Financial Information",
    #         {
    #             "fields": (
    #                 "amount",
    #                 "currency",
    #                 "amountUsd",
    #                 "createdAt",
    #                 "modifiedAt",
    #             )
    #         },
    #     ),
    #     (
    #         "Contact Information",
    #         {
    #             "fields": (
    #                 "email",
    #                 "phone",
    #                 "website",
    #                 "address",
    #                 "addressEntity",
    #             )
    #         },
    #     ),
    #     (
    #         "Other Information",
    #         {
    #             "fields": (
    #                 "wikidataId",
    #                 "keywords",
    #                 "topics",
    #                 "program",
    #                 "notes",
    #                 "cikCode",
    #                 "kppCode",
    #                 "bikCode",
    #                 "ticker",
    #                 "ricCode",
    #             )
    #         },
    #     ),
    #     ("Audit", {"fields": ("modifiedAt",)}),
    # )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Company Name"

    def country_display(self, obj):
        """Custom display for the 'country' field."""
        if isinstance(obj.country, list) and len(obj.country) == 1:
            return obj.country[0]
        return obj.country

    country_display.short_description = "Country"

    def status_display(self, obj):
        """Custom display for the 'status' field."""
        if isinstance(obj.status, list) and len(obj.status) == 1:
            return obj.status[0]
        return obj.status

    status_display.short_description = "Status"

    def sector_display(self, obj):
        """Custom display for the 'sector' field."""
        if isinstance(obj.sector, list) and len(obj.sector) == 1:
            return obj.sector[0]
        return obj.sector

    sector_display.short_description = "Sector"


@admin.register(Ownership)
class OwnershipAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "owner_display",
        "asset_display",
        "percentage_display",
        "status_display",
    )
    search_fields = (
        "owner",
        "asset",
        "role",
        "status",
        "percentage",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")  # Removed 'createdAt'
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Ownership Details",
            {
                "fields": (
                    "owner",
                    "asset",
                    "percentage",
                    "sharesCount",
                    "sharesValue",
                    "sharesCurrency",
                    "role",
                    "status",
                )
            },
        ),
        (
            "Audit and Dates",
            {
                "fields": (
                    "startDate",
                    "endDate",
                    "date",
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                    "modifiedAt",
                )
            },
        ),
    )

    def owner_display(self, obj):
        """Custom display for the 'owner' field."""
        if isinstance(obj.owner, list) and len(obj.owner) == 1:
            return obj.owner[0]
        return obj.owner

    owner_display.short_description = "Owner"

    def asset_display(self, obj):
        """Custom display for the 'asset' field."""
        if isinstance(obj.asset, list) and len(obj.asset) == 1:
            return obj.asset[0]
        return obj.asset

    asset_display.short_description = "Asset"

    def percentage_display(self, obj):
        """Custom display for the 'percentage' field."""
        if isinstance(obj.percentage, list) and len(obj.percentage) == 1:
            return obj.percentage[0]
        return obj.percentage

    percentage_display.short_description = "Percentage"

    def status_display(self, obj):
        """Custom display for the 'status' field."""
        if isinstance(obj.status, list) and len(obj.status) == 1:
            return obj.status[0]
        return obj.status

    status_display.short_description = "Status"


@admin.register(Vessel)
class VesselAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "imoNumber_display",
        "flag_display",
    )
    search_fields = (
        "name",
        "owner",
        "imoNumber",
        "flag",
        "registrationNumber",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt", "createdAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Vessel Information",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "registrationNumber",
                    "type",
                    "model",
                    "owner",
                    "buildDate",
                    "imoNumber",
                    "flag",
                    "tonnage",
                    "grossRegisteredTonnage",
                    "callSign",
                    "pastFlags",
                    "mmsi",
                )
            },
        ),
        (
            "Financials",
            {
                "fields": (
                    "amount",
                    "currency",
                    "amountUsd",
                )
            },
        ),
        (
            "Audit and Dates",
            {
                "fields": (
                    "createdAt",
                    "modifiedAt",
                    "sourceUrl",
                    "publisher",
                    "wikidataId",
                    "keywords",
                    "topics",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                )
            },
        ),
    )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"


    def imoNumber_display(self, obj):
        """Custom display for the 'imoNumber' field."""
        if isinstance(obj.imoNumber, list) and len(obj.imoNumber) == 1:
            return obj.imoNumber[0]
        return obj.imoNumber

    imoNumber_display.short_description = "IMO Number"

    def flag_display(self, obj):
        """Custom display for the 'flag' field."""
        if isinstance(obj.flag, list) and len(obj.flag) == 1:
            return obj.flag[0]
        return obj.flag

    flag_display.short_description = "Flag"


@admin.register(Position)
class PositionAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "inceptionDate_display",
        "dissolutionDate_display",
    )
    search_fields = (
        "name",
        "country",
        "inceptionDate",
        "dissolutionDate",
        "subnationalArea",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Position Information",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "inceptionDate",
                    "dissolutionDate",
                    "subnationalArea",
                )
            },
        ),
        (
            "Audit and Dates",
            {
                "fields": (
                    "createdAt",
                    "modifiedAt",
                    "sourceUrl",
                    "publisher",
                    "wikidataId",
                    "keywords",
                    "topics",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                )
            },
        ),
    )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"

    def inceptionDate_display(self, obj):
        """Custom display for the 'inceptionDate' field."""
        if isinstance(obj.inceptionDate, list) and len(obj.inceptionDate) == 1:
            return obj.inceptionDate[0]
        return obj.inceptionDate

    inceptionDate_display.short_description = "Inception Date"

    def dissolutionDate_display(self, obj):
        """Custom display for the 'dissolutionDate' field."""
        if isinstance(obj.dissolutionDate, list) and len(obj.dissolutionDate) == 1:
            return obj.dissolutionDate[0]
        return obj.dissolutionDate

    dissolutionDate_display.short_description = "Dissolution Date"


@admin.register(Asset)
class AssetAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "amount_display",
        "currency_display",
    )
    search_fields = (
        "name",
        "amount",
        "currency",
        "country",
        "amountUsd",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Asset Information",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "amount",
                    "currency",
                    "amountUsd",
                )
            },
        ),
        (
            "Audit and Dates",
            {
                "fields": (
                    "createdAt",
                    "modifiedAt",
                    "sourceUrl",
                    "publisher",
                    "wikidataId",
                    "keywords",
                    "topics",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                )
            },
        ),
    )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"

    def amount_display(self, obj):
        """Custom display for the 'amount' field."""
        if isinstance(obj.amount, list) and len(obj.amount) == 1:
            return obj.amount[0]
        return obj.amount

    amount_display.short_description = "Amount"

    def currency_display(self, obj):
        """Custom display for the 'currency' field."""
        if isinstance(obj.currency, list) and len(obj.currency) == 1:
            return obj.currency[0]
        return obj.currency

    currency_display.short_description = "Currency"


@admin.register(Associate)
class AssociateAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "relationship_display",
        "person_display",
        "associate_display",
    )
    search_fields = ("relationship", "person", "associate")
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Association Information",
            {
                "fields": (
                    "person",
                    "associate",
                    "relationship",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Details",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                    "modifiedAt",
                )
            },
        ),
    )

    def relationship_display(self, obj):
        """Custom display for the 'relationship' field."""
        if isinstance(obj.relationship, list) and len(obj.relationship) == 1:
            return obj.relationship[0]
        return obj.relationship

    relationship_display.short_description = "Relationship"

    def person_display(self, obj):
        """Custom display for the 'person' field."""
        if isinstance(obj.person, list) and len(obj.person) == 1:
            return obj.person[0]
        return obj.person

    person_display.short_description = "Person"

    def associate_display(self, obj):
        """Custom display for the 'associate' field."""
        if isinstance(obj.associate, list) and len(obj.associate) == 1:
            return obj.associate[0]
        return obj.associate

    associate_display.short_description = "Associate"


@admin.register(Identification)
class IdentificationAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "type_display",
        "number_display",
        "holder_display",
        "country_display",
    )
    search_fields = ("type", "number", "holder", "country")
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Identification Details",
            {
                "fields": (
                    "holder",
                    "type",
                    "number",
                    "country",
                    "authority",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Details",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                    "modifiedAt",
                )
            },
        ),
    )

    def type_display(self, obj):
        """Custom display for the 'type' field."""
        if isinstance(obj.type, list) and len(obj.type) == 1:
            return obj.type[0]
        return obj.type

    type_display.short_description = "Type"

    def number_display(self, obj):
        """Custom display for the 'number' field."""
        if isinstance(obj.number, list) and len(obj.number) == 1:
            return obj.number[0]
        return obj.number

    number_display.short_description = "Number"

    def holder_display(self, obj):
        """Custom display for the 'holder' field."""
        if isinstance(obj.holder, list) and len(obj.holder) == 1:
            return obj.holder[0]
        return obj.holder

    holder_display.short_description = "Holder"

    def country_display(self, obj):
        """Custom display for the 'country' field."""
        if isinstance(obj.country, list) and len(obj.country) == 1:
            return obj.country[0]
        return obj.country

    country_display.short_description = "Country"


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",

    )
    search_fields = (
        "name",
        "country",
        "status",
        "classification",
        "registrationNumber",
        "taxNumber",
        "email",
        "website",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "summary",
                    "description",
                    "country",
                    "mainCountry",
                )
            },
        ),
        (
            "Identifiers",
            {
                "fields": (
                    "registrationNumber",
                    "idNumber",
                    "taxNumber",
                    "vatCode",
                    "jurisdiction",
                    "icijId",
                    "leiCode",
                    "dunsCode",
                    "uniqueEntityId",
                    "npiCode",
                    "swiftBic",
                )
            },
        ),
        (
            "Codes and Numbers",
            {
                "fields": (
                    "okpoCode",
                    "innCode",
                    "ogrnCode",
                    "cageCode",
                    "permId",
                    "imoNumber",
                    "giiNumber",
                )
            },
        ),
        (
            "Dates and Status",
            {
                "fields": (
                    "incorporationDate",
                    "dissolutionDate",
                    "status",
                )
            },
        ),
        (
            "Additional Details",
            {
                "fields": (
                    "sector",
                    "classification",
                    "parent",
                    "notes",
                    "email",
                    "phone",
                    "website",
                )
            },
        ),
        (
            "Sources",
            {
                "fields": (
                    "sourceUrl",
                    "publisher",
                    "opencorporatesUrl",
                    "wikidataId",
                    "topics",
                    "keywords",
                    "address",
                    "addressEntity",
                    "program",
                    "createdAt",
                    "modifiedAt",
                )
            },
        ),
    )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"

    def country_display(self, obj):
        """Custom display for the 'country' field."""
        if isinstance(obj.country, list) and len(obj.country) == 1:
            return obj.country[0]
        return obj.country

    country_display.short_description = "Country"



@admin.register(Airplane)
class AirplaneAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "registrationNumber_display",
        "type_display",
        "owner_display",
    )
    search_fields = (
        "name",
        "registrationNumber",
        "type",
        "model",
        "owner",
        "serialNumber",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "summary",
                    "description",
                    "country",
                    "address",
                    "addressEntity",
                )
            },
        ),
        (
            "Identifiers",
            {
                "fields": (
                    "registrationNumber",
                    "serialNumber",
                    "wikidataId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Specifications",
            {
                "fields": (
                    "type",
                    "model",
                    "owner",
                    "buildDate",
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "amount",
                    "currency",
                    "amountUsd",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "program",
                    "topics",
                    "keywords",
                    "notes",
                    "createdAt",
                    "modifiedAt",
                )
            },
        ),
    )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"

    def registrationNumber_display(self, obj):
        """Custom display for the 'registrationNumber' field."""
        if (
            isinstance(obj.registrationNumber, list)
            and len(obj.registrationNumber) == 1
        ):
            return obj.registrationNumber[0]
        return obj.registrationNumber

    registrationNumber_display.short_description = "Registration Number"

    def type_display(self, obj):
        """Custom display for the 'type' field."""
        if isinstance(obj.type, list) and len(obj.type) == 1:
            return obj.type[0]
        return obj.type

    type_display.short_description = "Type"

    def owner_display(self, obj):
        """Custom display for the 'owner' field."""
        if isinstance(obj.owner, list) and len(obj.owner) == 1:
            return obj.owner[0]
        return obj.owner

    owner_display.short_description = "Owner"


@admin.register(PublicBody)
class PublicBodyAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        # "country_display",
        # "status_display",
        # "sector_display",
    )
    search_fields = (
        "name",
        "country",
        "alias",
        "registrationNumber",
        "idNumber",
        "taxNumber",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "summary",
                    "description",
                    "country",
                    "address",
                    "addressEntity",
                )
            },
        ),
        (
            "Contact Details",
            {
                "fields": (
                    "email",
                    "phone",
                    "website",
                )
            },
        ),
        (
            "Legal and Financial Information",
            {
                "fields": (
                    "legalForm",
                    "status",
                    "sector",
                    "classification",
                    "registrationNumber",
                    "idNumber",
                    "taxNumber",
                    "vatCode",
                    "jurisdiction",
                )
            },
        ),
        (
            "Additional Identifiers",
            {
                "fields": (
                    "opencorporatesUrl",
                    "icijId",
                    "okpoCode",
                    "innCode",
                    "ogrnCode",
                    "leiCode",
                    "dunsCode",
                    "uniqueEntityId",
                    "npiCode",
                    "swiftBic",
                    "cageCode",
                    "permId",
                    "imoNumber",
                    "giiNumber",
                )
            },
        ),
        (
            "Program and Notes",
            {
                "fields": (
                    "program",
                    "topics",
                    "keywords",
                    "notes",
                    "parent",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "createdAt",
                    "modifiedAt",
                )
            },
        ),
    )

    def name_display(self, obj):
        """Custom display for the 'name' field."""
        if isinstance(obj.name, list) and len(obj.name) == 1:
            return obj.name[0]
        return obj.name

    name_display.short_description = "Name"

    # def country_display(self, obj):
    #     """Custom display for the 'country' field."""
    #     if isinstance(obj.country, list) and len(obj.country) == 1:
    #         return obj.country[0]
    #     return obj.country

    # country_display.short_description = "Country"

    # def status_display(self, obj):
    #     """Custom display for the 'status' field."""
    #     if isinstance(obj.status, list) and len(obj.status) == 1:
    #         return obj.status[0]
    #     return obj.status

    # status_display.short_description = "Status"

    # def sector_display(self, obj):
    #     """Custom display for the 'sector' field."""
    #     if isinstance(obj.sector, list) and len(obj.sector) == 1:
    #         return obj.sector[0]
    #     return obj.sector

    # sector_display.short_description = "Sector"


@admin.register(Employment)
class EmploymentAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "role_display",
        "status_display",
        "employer_display",
        "employee_display",
    )
    search_fields = (
        "role",
        "status",
        "employer",
        "employee",
    )
    ordering = ("-sanctionEntity",)
    readonly_fields = ("sanctionEntity",)
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Employment Details",
            {
                "fields": (
                    "details",
                    "role",
                    "status",
                    "employer",
                    "employee",
                )
            },
        ),
    )

    def role_display(self, obj):
        return (
            obj.role[0]
            if isinstance(obj.role, list) and len(obj.role) == 1
            else obj.role
        )

    role_display.short_description = "Role"

    def status_display(self, obj):
        return (
            obj.status[0]
            if isinstance(obj.status, list) and len(obj.status) == 1
            else obj.status
        )

    status_display.short_description = "Status"

    def employer_display(self, obj):
        return (
            obj.employer[0]
            if isinstance(obj.employer, list) and len(obj.employer) == 1
            else obj.employer
        )

    employer_display.short_description = "Employer"

    def employee_display(self, obj):
        return (
            obj.employee[0]
            if isinstance(obj.employee, list) and len(obj.employee) == 1
            else obj.employee
        )

    employee_display.short_description = "Employee"


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "payer_display",
        "beneficiary_display",
        "amount_display",
        "currency_display",
        "date_display",
    )
    search_fields = (
        "payer",
        "beneficiary",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Payment Details",
            {
                "fields": (
                    "payer",
                    "beneficiary",
                    "amount",
                    "currency",
                    "amountUsd",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def payer_display(self, obj):
        return (
            obj.payer[0]
            if isinstance(obj.payer, list) and len(obj.payer) == 1
            else obj.payer
        )

    payer_display.short_description = "Payer"

    def beneficiary_display(self, obj):
        return (
            obj.beneficiary[0]
            if isinstance(obj.beneficiary, list) and len(obj.beneficiary) == 1
            else obj.beneficiary
        )

    beneficiary_display.short_description = "Beneficiary"

    def amount_display(self, obj):
        return (
            obj.amount[0]
            if isinstance(obj.amount, list) and len(obj.amount) == 1
            else obj.amount
        )

    amount_display.short_description = "Amount"

    def currency_display(self, obj):
        return (
            obj.currency[0]
            if isinstance(obj.currency, list) and len(obj.currency) == 1
            else obj.currency
        )

    currency_display.short_description = "Currency"

    def date_display(self, obj):
        return (
            obj.date[0]
            if isinstance(obj.date, list) and len(obj.date) == 1
            else obj.date
        )

    date_display.short_description = "Date"


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        # "name_display",
        "country_display",
        "city_display",
        "state_display",
    )
    search_fields = (
        "name",
        "country",
        "city",
        "state",
        "postalCode",
        "address",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Address Details",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "address",
                    "addressEntity",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "sourceUrl",
                    "publisher",
                    "wikidataId",
                    "keywords",
                    "topics",
                    "program",
                    "notes",
                )
            },
        ),
        (
            "Address Components",
            {
                "fields": (
                    "full",
                    "remarks",
                    "postOfficeBox",
                    "street",
                    "city",
                    "postalCode",
                    "region",
                    "state",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("createdAt", "modifiedAt")},
        ),
    )

    # def name_display(self, obj):
    #     return (
    #         obj.name[0]
    #         if isinstance(obj.name, list) and len(obj.name) == 1
    #         else obj.name
    #     )

    # name_display.short_description = "Name"

    def country_display(self, obj):
        return (
            obj.country[0]
            if isinstance(obj.country, list) and len(obj.country) == 1
            else obj.country
        )

    country_display.short_description = "Country"

    def city_display(self, obj):
        return (
            obj.city[0]
            if isinstance(obj.city, list) and len(obj.city) == 1
            else obj.city
        )

    city_display.short_description = "City"

    def state_display(self, obj):
        return (
            obj.state[0]
            if isinstance(obj.state, list) and len(obj.state) == 1
            else obj.state
        )

    state_display.short_description = "State"


@admin.register(Debt)
class DebtAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "debtor_display",
        "creditor_display",
        "amount_display",
        "currency_display",
        "date_display",
    )
    search_fields = (
        "debtor",
        "creditor",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Debt Details",
            {
                "fields": (
                    "debtor",
                    "creditor",
                    "amount",
                    "currency",
                    "amountUsd",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def debtor_display(self, obj):
        return (
            obj.debtor[0]
            if isinstance(obj.debtor, list) and len(obj.debtor) == 1
            else obj.debtor
        )

    debtor_display.short_description = "Debtor"

    def creditor_display(self, obj):
        return (
            obj.creditor[0]
            if isinstance(obj.creditor, list) and len(obj.creditor) == 1
            else obj.creditor
        )

    creditor_display.short_description = "Creditor"

    def amount_display(self, obj):
        return (
            obj.amount[0]
            if isinstance(obj.amount, list) and len(obj.amount) == 1
            else obj.amount
        )

    amount_display.short_description = "Amount"

    def currency_display(self, obj):
        return (
            obj.currency[0]
            if isinstance(obj.currency, list) and len(obj.currency) == 1
            else obj.currency
        )

    currency_display.short_description = "Currency"

    def date_display(self, obj):
        return (
            obj.date[0]
            if isinstance(obj.date, list) and len(obj.date) == 1
            else obj.date
        )

    date_display.short_description = "Date"


@admin.register(UnknownLink)
class UnknownLinkAdmin(ModelAdmin):
    list_display = (
        "subject_display",
        "object_display",
        "summary_display",
        "date_display",
    )
    search_fields = (
        "subject",
        "object",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Link Details",
            {
                "fields": (
                    "subject",
                    "object",
                    "role",
                    "status",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def subject_display(self, obj):
        return (
            obj.subject[0]
            if isinstance(obj.subject, list) and len(obj.subject) == 1
            else obj.subject
        )

    subject_display.short_description = "Subject"

    def object_display(self, obj):
        return (
            obj.object[0]
            if isinstance(obj.object, list) and len(obj.object) == 1
            else obj.object
        )

    object_display.short_description = "Object"

    def summary_display(self, obj):
        return (
            obj.summary[0]
            if isinstance(obj.summary, list) and len(obj.summary) == 1
            else obj.summary
        )

    summary_display.short_description = "Summary"

    def date_display(self, obj):
        return (
            obj.date[0]
            if isinstance(obj.date, list) and len(obj.date) == 1
            else obj.date
        )

    date_display.short_description = "Date"


@admin.register(Passport)
class PassportAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "holder_display",
        "number_display",
        "country_display",
        # "start_date_display",
        # "end_date_display",
    )
    search_fields = (
        "holder",
        "number",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Passport Details",
            {
                "fields": (
                    "holder",
                    "type",
                    "country",
                    "number",
                    "authority",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def holder_display(self, obj):
        return (
            obj.holder[0]
            if isinstance(obj.holder, list) and len(obj.holder) == 1
            else obj.holder
        )

    holder_display.short_description = "Holder"

    def number_display(self, obj):
        return (
            obj.number[0]
            if isinstance(obj.number, list) and len(obj.number) == 1
            else obj.number
        )

    number_display.short_description = "Number"

    def country_display(self, obj):
        return (
            obj.country[0]
            if isinstance(obj.country, list) and len(obj.country) == 1
            else obj.country
        )

    country_display.short_description = "Country"

    # def start_date_display(self, obj):
    #     return (
    #         obj.startDate[0]
    #         if isinstance(obj.startDate, list) and len(obj.startDate) == 1
    #         else obj.startDate
    #     )

    # start_date_display.short_description = "Start Date"

    # def end_date_display(self, obj):
    #     return (
    #         obj.endDate[0]
    #         if isinstance(obj.endDate, list) and len(obj.endDate) == 1
    #         else obj.endDate
    #     )

    # end_date_display.short_description = "End Date"


@admin.register(Representation)
class RepresentationAdmin(ModelAdmin):
    list_display = (
        "agent_display",
        "role_display",
        "client_display",
    )
    search_fields = (
        "agent",
        "client",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Representation Details",
            {
                "fields": (
                    "agent",
                    "client",
                    "role",
                    "status",
                    "startDate",
                    "endDate",
                    "date",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def agent_display(self, obj):
        return (
            obj.agent[0]
            if isinstance(obj.agent, list) and len(obj.agent) == 1
            else obj.agent
        )

    agent_display.short_description = "Agent"

    def client_display(self, obj):
        return (
            obj.client[0]
            if isinstance(obj.client, list) and len(obj.client) == 1
            else obj.client
        )

    client_display.short_description = "Client"

    def role_display(self, obj):
        return (
            obj.role[0]
            if isinstance(obj.role, list) and len(obj.role) == 1
            else obj.role
        )

    role_display.short_description = "Role"



@admin.register(Occupancy)
class OccupancyAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "holder_display",
        "post_display",
        "summary_display",
        "date_display",
    )
    search_fields = (
        "holder",
        "post",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Occupancy Details",
            {
                "fields": (
                    "holder",
                    "post",
                    "startDate",
                    "endDate",
                    "date",
                    "status",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def holder_display(self, obj):
        return (
            obj.holder[0]
            if isinstance(obj.holder, list) and len(obj.holder) == 1
            else obj.holder
        )

    holder_display.short_description = "Holder"

    def post_display(self, obj):
        return (
            obj.post[0]
            if isinstance(obj.post, list) and len(obj.post) == 1
            else obj.post
        )

    post_display.short_description = "Post"

    def summary_display(self, obj):
        return (
            obj.summary[0]
            if isinstance(obj.summary, list) and len(obj.summary) == 1
            else obj.summary
        )

    summary_display.short_description = "Summary"

    def date_display(self, obj):
        return (
            obj.date[0]
            if isinstance(obj.date, list) and len(obj.date) == 1
            else obj.date
        )

    date_display.short_description = "Date"


@admin.register(Membership)
class MembershipAdmin(ModelAdmin):
    list_display = (
        "member_display",
        "role_display",
        "organization_display",
    )
    search_fields = (
        "role",
        "member",
        "organization",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Membership Details",
            {
                "fields": (
                    "member",
                    "organization",
                    "role",
                    "startDate",
                    "endDate",
                    "date",
                    "status",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def member_display(self, obj):
        return (
            obj.member[0]
            if isinstance(obj.member, list) and len(obj.member) == 1
            else obj.member
        )

    member_display.short_description = "Member"

    def organization_display(self, obj):
        return (
            obj.organization[0]
            if isinstance(obj.organization, list) and len(obj.organization) == 1
            else obj.organization
        )

    organization_display.short_description = "Organization"

    def role_display(self, obj):
        return (
            obj.role[0]
            if isinstance(obj.role, list) and len(obj.role) == 1
            else obj.role
        )

    role_display.short_description = "Role"



@admin.register(Directorship)
class DirectorshipAdmin(ModelAdmin):
    list_display = (
        # "sanctionEntity",
        "director_display",
        "organization_display",
        "role_display",
        "summary_display",
        "date_display",
    )
    search_fields = (
        "role",
        "director",
        "organization",
        "summary",
        "description",
        "recordId",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Directorship Details",
            {
                "fields": (
                    "director",
                    "organization",
                    "role",
                    "startDate",
                    "endDate",
                    "date",
                    "status",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("modifiedAt",)},
        ),
    )

    def director_display(self, obj):
        return (
            obj.director[0]
            if isinstance(obj.director, list) and len(obj.director) == 1
            else obj.director
        )

    director_display.short_description = "Director"

    def organization_display(self, obj):
        return (
            obj.organization[0]
            if isinstance(obj.organization, list) and len(obj.organization) == 1
            else obj.organization
        )

    organization_display.short_description = "Organization"

    def role_display(self, obj):
        return (
            obj.role[0]
            if isinstance(obj.role, list) and len(obj.role) == 1
            else obj.role
        )

    role_display.short_description = "Role"

    def summary_display(self, obj):
        return (
            obj.summary[0]
            if isinstance(obj.summary, list) and len(obj.summary) == 1
            else obj.summary
        )

    summary_display.short_description = "Summary"

    def date_display(self, obj):
        return (
            obj.date[0]
            if isinstance(obj.date, list) and len(obj.date) == 1
            else obj.date
        )

    date_display.short_description = "Date"


@admin.register(LegalEntity)
class LegalEntityAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",
        "status_display",
    
    )
    search_fields = (
        "name",
        "country",
        "alias",
        "previousName",
        "address",
        "program",
        "keywords",
        "notes",
        "email",
        "phone",
        "website",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Legal Entity Details",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "phone",
                    "website",
                    "opencorporatesUrl",
                    "icijId",
                )
            },
        ),
        (
            "Legal and Regulatory Information",
            {
                "fields": (
                    "legalForm",
                    "incorporationDate",
                    "dissolutionDate",
                    "status",
                    "sector",
                    "classification",
                    "registrationNumber",
                    "idNumber",
                    "taxNumber",
                    "vatCode",
                    "jurisdiction",
                )
            },
        ),
        (
            "Financial and Identification Information",
            {
                "fields": (
                    "mainCountry",
                    "okpoCode",
                    "innCode",
                    "ogrnCode",
                    "leiCode",
                    "dunsCode",
                    "uniqueEntityId",
                    "npiCode",
                    "swiftBic",
                    "parent",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("createdAt", "modifiedAt")},
        ),
    )

    def name_display(self, obj):
        return (
            obj.name[0]
            if isinstance(obj.name, list) and len(obj.name) == 1
            else obj.name
        )

    name_display.short_description = "Name"

    def country_display(self, obj):
        return (
            obj.country[0]
            if isinstance(obj.country, list) and len(obj.country) == 1
            else obj.country
        )

    country_display.short_description = "Country"

    def status_display(self, obj):
        return (
            obj.status[0]
            if isinstance(obj.status, list) and len(obj.status) == 1
            else obj.status
        )

    status_display.short_description = "Status"


@admin.register(Security)
class SecurityAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",
      
    )
    search_fields = (
        "name",
        "country",
        
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Security Details",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "amount",
                    "currency",
                    "amountUsd",
                    "isin",
                    "registrationNumber",
                    "ticker",
                    "figiCode",
                    "issuer",
                    "issueDate",
                    "maturityDate",
                    "type",
                    "classification",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("createdAt", "modifiedAt")},
        ),
    )

    def name_display(self, obj):
        return (
            obj.name[0]
            if isinstance(obj.name, list) and len(obj.name) == 1
            else obj.name
        )

    name_display.short_description = "Name"

    def country_display(self, obj):
        return (
            obj.country[0]
            if isinstance(obj.country, list) and len(obj.country) == 1
            else obj.country
        )

    country_display.short_description = "Country"



@admin.register(Interval)
class IntervalAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "summary_display",
        "startDate_display",
        "endDate_display",
        "modifiedAt_display",
    )
    search_fields = (
        "summary",
        "description",
        "recordId",
        "sourceUrl",
        "publisher",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Interval Details",
            {
                "fields": (
                    "startDate",
                    "endDate",
                    "date",
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        ("Timestamps", {"fields": ("modifiedAt",)}),
    )

    def summary_display(self, obj):
        return (
            obj.summary[0]
            if isinstance(obj.summary, list) and len(obj.summary) == 1
            else obj.summary
        )

    summary_display.short_description = "Summary"

    def startDate_display(self, obj):
        return (
            obj.startDate[0]
            if isinstance(obj.startDate, list) and len(obj.startDate) == 1
            else obj.startDate
        )

    startDate_display.short_description = "Start Date"

    def endDate_display(self, obj):
        return (
            obj.endDate[0]
            if isinstance(obj.endDate, list) and len(obj.endDate) == 1
            else obj.endDate
        )

    endDate_display.short_description = "End Date"

    def modifiedAt_display(self, obj):
        return (
            obj.modifiedAt[0]
            if isinstance(obj.modifiedAt, list) and len(obj.modifiedAt) == 1
            else obj.modifiedAt
        )

    modifiedAt_display.short_description = "Modified At"


@admin.register(Thing)
class ThingAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",
        "createdAt_display",
        "modifiedAt_display",
    )
    search_fields = (
        "name",
        "summary",
        "description",
        "address",
        "program",
        "keywords",
        "topics",
        "notes",
        "createdAt",
        "modifiedAt",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Thing Details",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                )
            },
        ),
        ("Timestamps", {"fields": ("createdAt", "modifiedAt")}),
    )

    def name_display(self, obj):
        return (
            obj.name[0]
            if isinstance(obj.name, list) and len(obj.name) == 1
            else obj.name
        )

    name_display.short_description = "Name"

    def country_display(self, obj):
        return (
            obj.country[0]
            if isinstance(obj.country, list) and len(obj.country) == 1
            else obj.country
        )

    country_display.short_description = "Country"

    def createdAt_display(self, obj):
        return (
            obj.createdAt[0]
            if isinstance(obj.createdAt, list) and len(obj.createdAt) == 1
            else obj.createdAt
        )

    createdAt_display.short_description = "Created At"

    def modifiedAt_display(self, obj):
        return (
            obj.modifiedAt[0]
            if isinstance(obj.modifiedAt, list) and len(obj.modifiedAt) == 1
            else obj.modifiedAt
        )

    modifiedAt_display.short_description = "Modified At"


@admin.register(Value)
class ValueAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "amount_display",
        "currency_display",
        "amountUsd_display",
    )
    search_fields = (
        "amount",
        "currency",
        "amountUsd",
    )
    ordering = ("-sanctionEntity",)
    readonly_fields = ("sanctionEntity",)
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        ("Value Details", {"fields": ("amount", "currency", "amountUsd")}),
    )

    def amount_display(self, obj):
        return (
            obj.amount[0]
            if isinstance(obj.amount, list) and len(obj.amount) == 1
            else obj.amount
        )

    amount_display.short_description = "Amount"

    def currency_display(self, obj):
        return (
            obj.currency[0]
            if isinstance(obj.currency, list) and len(obj.currency) == 1
            else obj.currency
        )

    currency_display.short_description = "Currency"

    def amountUsd_display(self, obj):
        return (
            obj.amountUsd[0]
            if isinstance(obj.amountUsd, list) and len(obj.amountUsd) == 1
            else obj.amountUsd
        )

    amountUsd_display.short_description = "Amount USD"


@admin.register(Interest)
class InterestAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "summary_display",
        "startDate_display",
        "endDate_display",
        "modifiedAt_display",
    )
    search_fields = (
        "summary",
        "description",
        "recordId",
        "sourceUrl",
        "publisher",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Interest Details",
            {
                "fields": (
                    "startDate",
                    "endDate",
                    "date",
                    "summary",
                    "description",
                    "recordId",
                    "sourceUrl",
                    "publisher",
                )
            },
        ),
        ("Timestamps", {"fields": ("modifiedAt",)}),
    )

    def summary_display(self, obj):
        return (
            obj.summary[0]
            if isinstance(obj.summary, list) and len(obj.summary) == 1
            else obj.summary
        )

    summary_display.short_description = "Summary"

    def startDate_display(self, obj):
        return (
            obj.startDate[0]
            if isinstance(obj.startDate, list) and len(obj.startDate) == 1
            else obj.startDate
        )

    startDate_display.short_description = "Start Date"

    def endDate_display(self, obj):
        return (
            obj.endDate[0]
            if isinstance(obj.endDate, list) and len(obj.endDate) == 1
            else obj.endDate
        )

    endDate_display.short_description = "End Date"

    def modifiedAt_display(self, obj):
        return (
            obj.modifiedAt[0]
            if isinstance(obj.modifiedAt, list) and len(obj.modifiedAt) == 1
            else obj.modifiedAt
        )

    modifiedAt_display.short_description = "Modified At"


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    list_display = (
        "sanctionEntity",
        "name_display",
        "country_display",
        "createdAt_display",
        "modifiedAt_display",
    )
    search_fields = (
        "name",
        "summary",
        "description",
        "address",
        "program",
        "keywords",
        "topics",
        "notes",
        "createdAt",
        "modifiedAt",
        "amount",
        "currency",
        "amountUsd",
        "registrationNumber",
        "type",
        "model",
        "owner",
        "buildDate",
    )
    ordering = ("-modifiedAt",)
    readonly_fields = ("sanctionEntity", "createdAt", "modifiedAt")
    fieldsets = (
        ("Sanctioned Entity", {"fields": ("sanctionEntity",)}),
        (
            "Vehicle Details",
            {
                "fields": (
                    "name",
                    "summary",
                    "description",
                    "country",
                    "alias",
                    "previousName",
                    "weakAlias",
                    "address",
                    "addressEntity",
                    "program",
                    "notes",
                    "amount",
                    "currency",
                    "amountUsd",
                    "registrationNumber",
                    "type",
                    "model",
                    "owner",
                    "buildDate",
                )
            },
        ),
        ("Timestamps", {"fields": ("createdAt", "modifiedAt")}),
    )

    def name_display(self, obj):
        return (
            obj.name[0]
            if isinstance(obj.name, list) and len(obj.name) == 1
            else obj.name
        )

    name_display.short_description = "Name"

    def country_display(self, obj):
        return (
            obj.country[0]
            if isinstance(obj.country, list) and len(obj.country) == 1
            else obj.country
        )

    country_display.short_description = "Country"

    def createdAt_display(self, obj):
        return (
            obj.createdAt[0]
            if isinstance(obj.createdAt, list) and len(obj.createdAt) == 1
            else obj.createdAt
        )

    createdAt_display.short_description = "Created At"

    def modifiedAt_display(self, obj):
        return (
            obj.modifiedAt[0]
            if isinstance(obj.modifiedAt, list) and len(obj.modifiedAt) == 1
            else obj.modifiedAt
        )

    modifiedAt_display.short_description = "Modified At"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "gender", "dob", "organization", "photo", 
                    'created_at', 'updated_at')
    search_fields = ("user__username", "phone", "organization")
    list_filter = ("gender", "dob")
    actions = ['delete_selected'] 
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "phone", "dob", "gender", 
                    "nationality", "address", "photo", 'status', 
                    'created_at', 'updated_at')
    
@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_id", "id_type", "id_number", "issuing_country",  "issue_date", "expiry_date", "document", 
                    'created_at', 'updated_at')
    
@admin.register(Employability)
class EmployabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_id", "status", "occupation", "employer_name",  "employer_address", "annual_income", 
                    'created_at', 'updated_at')
    
@admin.register(BankInfo)
class BankInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_id", "bank_name", "account_number", "account_type", "swift_code_iban",  
                    'created_at', 'updated_at')
    
@admin.register(CustomerAdditionalInfo)
class CustomerAdditionalInfo(admin.ModelAdmin):
    list_display = ("id", "customer_id", "account_purpose", "expected_transactions", "annual_turnover", "fund_source", "pep_status",  
                    'created_at', 'updated_at')
    
@admin.register(BusinessInfo)
class BusinessInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_id", "business_type", "business_name", "regi_number", "incorporation_date", "incorporation_country", 
                    "registered_address", "operational_address", "phone", "email", "website", 
                    "industry_sector", "key_products_services", "business_activities_desc", 
                    'created_at', 'updated_at')

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_id", "id_type", "document", 'status', 
                    'created_at', 'updated_at')

@admin.register(FlagApproval)
class FlagApprovalAdmin(admin.ModelAdmin):
    list_display = ("id", "verification_id", 'status', 
                    "reason_type", 'details', "forwarded_to", "forward_message", 
                    'created_at', 'updated_at')
    
@admin.register(ResearchRequest)
class ResearchRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_id", "document", 'status', 
                    'priority', "research_type", "subject", "description",
                    'created_at', 'updated_at')

@admin.register(ActivityLogs)
class ActivityLogsAdmin(admin.ModelAdmin):
    list_display = ("id", 'activity', 'description', 'ip_address', 'country', 'city', 'status', 
                    'created_at', 'updated_at')
    list_filter = ('activity', 'status', 'country', 'city')
    search_fields = ('description', 'ip_address', 'country', 'city', 'user__username')
    ordering = ('-updated_at',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'query', 'result_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query', 'user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
