from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CandidatureViewSet, dashboard_view, dashboard_stats_api, dashboard_charts_data,
    create_candidature_view, my_candidatures_view, candidatures_list_view,
    candidature_detail_view, edit_candidature_view
)

app_name = 'candidatures'
from .views import CandidatureViewSet
from . import ai_views

router = DefaultRouter()
router.register(r'candidatures', CandidatureViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/dashboard/stats/', dashboard_stats_api, name='dashboard-stats-api'),
    path('api/dashboard/charts/', dashboard_charts_data, name='dashboard-charts-api'),
    
    # Template-based views
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create/', create_candidature_view, name='create'),
    path('my-candidatures/', my_candidatures_view, name='my_candidatures'),
    path('list/', candidatures_list_view, name='list'),
    path('<int:pk>/', candidature_detail_view, name='detail'),
    path('<int:pk>/edit/', edit_candidature_view, name='edit'),
    path('candidatures/<int:candidature_id>/analyze/', ai_views.analyze_cv, name='analyze_cv'),
    path('candidatures/<int:candidature_id>/analysis/', ai_views.get_analysis_results, name='get_analysis_results'),
    path('test/preprocess/', ai_views.preprocess_cv_test, name='preprocess_test'),
]
