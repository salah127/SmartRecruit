from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailPreferencesViewSet, EmailNotificationLogViewSet

router = DefaultRouter()
router.register(r'preferences', EmailPreferencesViewSet, basename='email-preferences')
router.register(r'logs', EmailNotificationLogViewSet, basename='notification-logs')

urlpatterns = [
    path('api/', include(router.urls)),
]
