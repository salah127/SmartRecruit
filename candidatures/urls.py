from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidatureViewSet

router = DefaultRouter()
router.register(r'candidatures', CandidatureViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
