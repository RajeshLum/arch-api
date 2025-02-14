import os
from datetime import timedelta
from pathlib import Path

from decouple import config
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = ["*"]

 
INSTALLED_APPS = [
    "unfold",
    "rest_framework",
    "djoser",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "data",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "archangel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "archangel.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = "static/"

CSRF_TRUSTED_ORIGINS = [
    "https://api.angefin.com",
    "https://www.api.angefin.com",
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = [
    "127.0.0.1",
    "103.160.107.11",
    "0.0.0.0",
]


UNFOLD = {
    "SITE_TITLE": "Arch Angel Data Lake",
    "SITE_HEADER": "Arch Angel",
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "data.views.admin_dashboard.dashboard_callback",
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Authentication and Authorization",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "account_circle",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "auth.view_user"
                        ),
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "auth.view_group"
                        ),
                    },
                ],
            },
            {
                "title": "Data",
                "separator": True,
                "items": [
                    {
                        "title": "Sanctioned Entities",
                        "icon": "stacks",
                        "link": reverse_lazy("admin:data_sanctionedentity_changelist"),
                    },
                ],
            },
            {
                "title": "Data Schema",
                "separator": True,
                "items": [
                    {
                        "title": "Address",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:data_address_changelist"),
                    },
                    {
                        "title": "Airplane",
                        "icon": "flight",
                        "link": reverse_lazy("admin:data_airplane_changelist"),
                    },
                    {
                        "title": "Asset",
                        "icon": "factory",
                        "link": reverse_lazy("admin:data_asset_changelist"),
                    },
                    {
                        "title": "Associate",
                        "icon": "hub",
                        "link": reverse_lazy("admin:data_associate_changelist"),
                    },
                    {
                        "title": "Company",
                        "icon": "apartment",
                        "link": reverse_lazy("admin:data_company_changelist"),
                    },
                    {
                        "title": "Crypto Wallet",
                        "icon": "account_balance_wallet",
                        "link": reverse_lazy("admin:data_cryptowallet_changelist"),
                    },
                    {
                        "title": "Debt",
                        "icon": "payments",
                        "link": reverse_lazy("admin:data_debt_changelist"),
                    },
                    {
                        "title": "Directorship",
                        "icon": "event_seat",
                        "link": reverse_lazy("admin:data_directorship_changelist"),
                    },
                    {
                        "title": "Employment",
                        "icon": "handshake",
                        "link": reverse_lazy("admin:data_employment_changelist"),
                    },
                    {
                        "title": "Family",
                        "icon": "family_restroom",
                        "link": reverse_lazy("admin:data_family_changelist"),
                    },
                    {
                        "title": "Identification",
                        "icon": "fingerprint",
                        "link": reverse_lazy("admin:data_identification_changelist"),
                    },
                    {
                        "title": "Interest",
                        "icon": "interests",
                        "link": reverse_lazy("admin:data_interest_changelist"),
                    },
                    {
                        "title": "Interval",
                        "icon": "schedule",
                        "link": reverse_lazy("admin:data_interval_changelist"),
                    },
                    {
                        "title": "Legal Entity",
                        "icon": "gavel",
                        "link": reverse_lazy("admin:data_legalentity_changelist"),
                    },
                    {
                        "title": "Membership",
                        "icon": "person_add",
                        "link": reverse_lazy("admin:data_membership_changelist"),
                    },
                    {
                        "title": "Occupancy",
                        "icon": "sensor_occupied",
                        "link": reverse_lazy("admin:data_occupancy_changelist"),
                    },
                    {
                        "title": "Organization",
                        "icon": "corporate_fare",
                        "link": reverse_lazy("admin:data_organization_changelist"),
                    },
                    {
                        "title": "Passport",
                        "icon": "id_card",
                        "link": reverse_lazy("admin:data_passport_changelist"),
                    },
                    {
                        "title": "Payment",
                        "icon": "attach_money",
                        "link": reverse_lazy("admin:data_payment_changelist"),
                    },
                    {
                        "title": "Person",
                        "icon": "person",
                        "link": reverse_lazy("admin:data_person_changelist"),
                    },
                    {
                        "title": "Position",
                        "icon": "mountain_flag",
                        "link": reverse_lazy("admin:data_position_changelist"),
                    },
                    {
                        "title": "Public Body",
                        "icon": "public",
                        "link": reverse_lazy("admin:data_publicbody_changelist"),
                    },
                    {
                        "title": "Representation",
                        "icon": "language_japanese_kana",
                        "link": reverse_lazy("admin:data_representation_changelist"),
                    },
                    {
                        "title": "Sanction",
                        "icon": "crossword",
                        "link": reverse_lazy("admin:data_sanction_changelist"),
                    },
                    {
                        "title": "Security",
                        "icon": "lock",
                        "link": reverse_lazy("admin:data_security_changelist"),
                    },
                    {
                        "title": "Succession",
                        "icon": "package",
                        "link": reverse_lazy("admin:data_succession_changelist"),
                    },
                    {
                        "title": "Thing",
                        "icon": "deployed_code",
                        "link": reverse_lazy("admin:data_thing_changelist"),
                    },
                    {
                        "title": "Unknown Link",
                        "icon": "link",
                        "link": reverse_lazy("admin:data_unknownlink_changelist"),
                    },
                    {
                        "title": "Value",
                        "icon": "sell",
                        "link": reverse_lazy("admin:data_value_changelist"),
                    },
                    {
                        "title": "Vehicle",
                        "icon": "local_shipping",
                        "link": reverse_lazy("admin:data_vehicle_changelist"),
                    },
                    {
                        "title": "Vessel",
                        "icon": "directions_boat",
                        "link": reverse_lazy("admin:data_vessel_changelist"),
                    },
                ],
            },
        ],
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

}

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
   'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

}



SPECTACULAR_SETTINGS = {
    'TITLE': 'Arch Angel Datalake',
    'DESCRIPTION': 'Backend API endpoints of ArchAngel Datalake',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}