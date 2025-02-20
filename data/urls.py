from django.urls import path

from data.views.batch_processing2 import BatchStatusView, UploadDataView
from data.views.entity_details import EntityDetailView
from data.views.ocr import PassportOCRView
from data.views.ocr_aml import PassportOCRLookup
from data.views.reconcile import ReconcileView

from .views.match_entities import MatchEntitiesView
from .views.risk_scoring import RiskScoringView
from .views.risk_scoring_id import RiskDetailsView
from .views.search_entities import SearchEntitiesView

urlpatterns = [
    path('match/', MatchEntitiesView.as_view(), name='match-entities'),
    path('search/', SearchEntitiesView.as_view(), name='search-entities'),
    path('entities/<str:entity_id>/', EntityDetailView.as_view(), name='entity-detail'),
    path('aml/risk/score', RiskScoringView.as_view(), name='risk-score'),
    path('aml/risk/details/<str:entity_id>', RiskDetailsView.as_view(), name='risk-details'),
    path('batch-upload/', UploadDataView.as_view(), name='batch-upload'),
    path('batch-status/<str:batch_id>/', BatchStatusView.as_view(), name='batch-status'),
    path('reconcile/', ReconcileView.as_view(), name='reconcile-entities'),
    path('ocr/extract/', PassportOCRView.as_view(), name='extract-passport'),
    path('ocr/lookup/', PassportOCRLookup.as_view(), name='extract-passport'),
]
