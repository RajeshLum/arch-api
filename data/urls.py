from django.urls import path

from .views import MatchEntitiesView, RiskScoringView, SearchEntitiesView

urlpatterns = [
    path('api/match/', MatchEntitiesView.as_view(), name='match-entities'),
    path('api/search/', SearchEntitiesView.as_view(), name='search-entities'),
    path('api/aml/risk/score', RiskScoringView.as_view(), name='risk-score'),

]
