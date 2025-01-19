from django.urls import path

from .views import MatchEntitiesView

urlpatterns = [
    path('api/match/', MatchEntitiesView.as_view(), name='match-entities'),
]
