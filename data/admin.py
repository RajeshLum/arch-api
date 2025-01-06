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
        "gender",
        "nationality",
    )
    list_filter = (PersonGenderFilter,)
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


@admin.register(Sanction)
class SanctionAdmin(ModelAdmin):
    list_display = ("sanctionEntity", "entity", "startDate", "endDate", "country")
    search_fields = (
        "entity",
        "recordId",
        "sourceUrl",
        "authority",
        "unscId",
        "program",
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


@admin.register(Family)
class FamilyAdmin(ModelAdmin):
    list_display = ("sanctionEntity__sanctionId", "person", "relative")
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


@admin.register(CryptoWallet)
class CryptoWalletAdmin(ModelAdmin):
    list_display = ("sanctionEntity", "currency", "holder", "publicKey")
    search_fields = (
        "name",
        "alias",
        "previousName",
        "sourceUrl",
        "address",
        "publicKey",
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
        "status",
        "sector",
    )
    ordering = ("-modifiedAt",)
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
        "owner_display",
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

    def owner_display(self, obj):
        """Custom display for the 'owner' field."""
        if isinstance(obj.owner, list) and len(obj.owner) == 1:
            return obj.owner[0]
        return obj.owner

    owner_display.short_description = "Owner"

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
