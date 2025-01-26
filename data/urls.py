from django.urls import path

from .views.match_entities import MatchEntitiesView
from .views.risk_scoring import RiskScoringView
from .views.search_entities import SearchEntitiesView

urlpatterns = [
    path('api/match/', MatchEntitiesView.as_view(), name='match-entities'),
    path('api/search/', SearchEntitiesView.as_view(), name='search-entities'),
    path('api/aml/risk/score', RiskScoringView.as_view(), name='risk-score'),
]
