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
        "DIRS": [],
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


STATIC_URL = "static/"


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
    # "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
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
                "title": "Data Category",
                "separator": True,
                "items": [
                    {
                        "title": "Person",
                        "icon": "person",
                        "link": reverse_lazy("admin:data_person_changelist"),
                    },
                    {
                        "title": "Family",
                        "icon": "family_restroom",
                        "link": reverse_lazy("admin:data_family_changelist"),
                    },
                    {
                        "title": "Sanction",
                        "icon": "crossword",
                        "link": reverse_lazy("admin:data_sanction_changelist"),
                    },
                    {
                        "title": "Crypto Wallet",
                        "icon": "account_balance_wallet",
                        "link": reverse_lazy("admin:data_cryptowallet_changelist"),
                    },
                    {
                        "title": "Succession",
                        "icon": "package",
                        "link": reverse_lazy("admin:data_succession_changelist"),
                    },
                    {
                        "title": "Company",
                        "icon": "apartment",
                        "link": reverse_lazy("admin:data_company_changelist"),
                    },
                    {
                        "title": "Ownership",
                        "icon": "badge",
                        "link": reverse_lazy("admin:data_ownership_changelist"),
                    },
                    {
                        "title": "Vessel",
                        "icon": "directions_boat",
                        "link": reverse_lazy("admin:data_vessel_changelist"),
                    },
                    {
                        "title": "Position",
                        "icon": "mountain_flag",
                        "link": reverse_lazy("admin:data_position_changelist"),
                    },
                    {
                        "title": "Asset",
                        "icon": "factory",
                        "link": reverse_lazy("admin:data_asset_changelist"),
                    },
                ],
            },
        ],
    },
    # "TABS": [
    #     {
    #         "models": [
    #             "app_label.model_name_in_lowercase",
    #         ],
    #         "items": [
    #             {
    #                 "title": _("Your custom title"),
    #                 "link": reverse_lazy("admin:app_label_model_name_changelist"),
    #                 "permission": "sample_app.permission_callback",
    #             },
    #         ],
    #     },
    # ],
}


# def dashboard_callback(request, context):
#     """
#     Callback to prepare custom variables for index template which is used as dashboard
#     template. It can be overridden in application by creating custom admin/index.html.
#     """
#     context.update(
#         {
#             "sample": "example",  # this will be injected into templates/admin/index.html
#         }
#     )
#     return context
