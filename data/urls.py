from django.urls import path

from data.views.batch_processing import BatchStatusView, UploadDataView
from data.views.entity_details import EntityDetailView

from .views.match_entities import MatchEntitiesView
from .views.risk_scoring import RiskScoringView
from .views.risk_scoring_id import RiskDetailsView
from .views.search_entities import SearchEntitiesView

urlpatterns = [
    path('api/match/', MatchEntitiesView.as_view(), name='match-entities'),
    path('api/search/', SearchEntitiesView.as_view(), name='search-entities'),
    path('api/entities/<str:entity_id>/', EntityDetailView.as_view(), name='entity-detail'),
    path('api/aml/risk/score', RiskScoringView.as_view(), name='risk-score'),
    path('api/aml/risk/details/<str:entity_id>', RiskDetailsView.as_view(), name='risk-details'),
    path('api/batch-upload/', UploadDataView.as_view(), name='batch-upload'),
    path('api/batch-status/<str:batch_id>/', BatchStatusView.as_view(), name='batch-status'),
]
