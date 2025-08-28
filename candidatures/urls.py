from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidatureViewSet
from . import ai_views

router = DefaultRouter()
router.register(r'candidatures', CandidatureViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('candidatures/<int:candidature_id>/analyze/', ai_views.analyze_cv, name='analyze_cv'),
    path('candidatures/<int:candidature_id>/analysis/', ai_views.get_analysis_results, name='get_analysis_results'),
    path('test/preprocess/', ai_views.preprocess_cv_test, name='preprocess_test'),
]
