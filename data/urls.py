from django.urls import path

from .views.match_entities import MatchEntitiesView
from data.views.entity_details import EntityDetailView
from .views.search_entities import SearchEntitiesView

from data.views.batch_processing2 import UploadDataView, BatchStatusView
from data.views.reconcile import ReconcileView

from .views.risk_scoring import RiskScoringView
from .views.risk_scoring_id import RiskDetailsView
from data.views.ocr import PassportOCRView
from data.views.ocr_aml import PassportOCRLookup

from data.views.user.profile import ProfileView
from data.views.user.update_password import UpdatePasswordView

from data.views.customer.customer_registration import CustomerListCreateView, CustomerDetailView
from data.views.verification.verify_document import VerificationListCreateView, VerificationDetailView
from data.views.flag_approval import FlagApprovalListCreateView, FlagApprovalDetailView
from data.views.research_request import ResearchRequestListCreateView, ResearchRequestDetailView

from data.views.activity_logs import ActivityLogsView
from data.views.dashboard_statistics import DashboardStatisticsView
from data.views.search_history import SearchHistoryListCreateView, SearchHistoryDetailView, SearchHistoryClearView, RecentSearchHistoryView

urlpatterns = [
    path('match/', MatchEntitiesView.as_view(), name='match-entities'), # post
    path('entities/<str:entity_id>/', EntityDetailView.as_view(), name='entity-detail'), # get
    path('search/', SearchEntitiesView.as_view(), name='search-entities'), # get
    
    # batch SanctionedEntity
    path('batch-upload/', UploadDataView.as_view(), name='batch-upload'), # post
    path('batch-status/<str:batch_id>/', BatchStatusView.as_view(), name='batch-status'), # get
    
    # reconcile
    path('reconcile/', ReconcileView.as_view(), name='reconcile-entities'), # get
    
    # aml
    path('aml/risk/score', RiskScoringView.as_view(), name='risk-score'), # post
    path('aml/risk/details/<str:entity_id>', RiskDetailsView.as_view(), name='risk-details'), # get
    
    # ocr to aml
    path('ocr/extract/', PassportOCRView.as_view(), name='extract-passport'), # post
    path('ocr/lookup/', PassportOCRLookup.as_view(), name='extract-passport'), # post
    
    # profile
    path('profile/', ProfileView.as_view(), name='profile'), # get, put
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'), # post
    
    # customers
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    
    # verifications
    path('verifications/', VerificationListCreateView.as_view(), name='verification-list-create'),
    path('verifications/<int:pk>/', VerificationDetailView.as_view(), name='verification-detail'),
    
    # flag & approval
    path('flag-approvals/', FlagApprovalListCreateView.as_view(), name='flag-approval-list-create'),
    path('flag-approvals/<int:pk>/', FlagApprovalDetailView.as_view(), name='flag-approval-detail'),
    
    # research request
    path('research-requests/', ResearchRequestListCreateView.as_view(), name='research-request-list-create'),
    path('research-requests/<int:pk>/', ResearchRequestDetailView.as_view(), name='research-request-detail'),
    
    # activity logs
    path('activity-logs/', ActivityLogsView.as_view(), name='activity-logs'), # get, post, delete
    
    # dashboard statistics
    path('dashboard/statistics/', DashboardStatisticsView.as_view(), name='dashboard-statistics'), # get
    
    # search history
    path('search-history/', SearchHistoryListCreateView.as_view(), name='search-history-list-create'),
    path('search-history/<int:pk>/', SearchHistoryDetailView.as_view(), name='search-history-detail'),
    path('search-history/clear/', SearchHistoryClearView.as_view(), name='search-history-clear'),
    path('search-history/recent/', RecentSearchHistoryView.as_view(), name='search-history-recent'),
]
