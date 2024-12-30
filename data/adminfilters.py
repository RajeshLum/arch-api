from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class PersonGenderFilter(admin.SimpleListFilter):
    """Gender Filter for Person Object"""

    title = _("Gender")
    parameter_name = "gender"

    def lookups(self, request, model_admin):
        return [
            ("male", _("Male")),
            ("female", _("Female")),
            ("other", _("Other")),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(gender__contains=self.value())
        return queryset
