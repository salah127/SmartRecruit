from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EmailPreferences, EmailNotificationLog
from .serializers import EmailPreferencesSerializer, EmailNotificationLogSerializer


class EmailPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email preferences
    """
    serializer_class = EmailPreferencesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only return current user's preferences"""
        return EmailPreferences.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create preferences for current user"""
        preferences, created = EmailPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's email preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_preferences(self, request):
        """Update current user's email preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailNotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing email notification logs (read-only)
    """
    serializer_class = EmailNotificationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs based on user role"""
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all logs
            return EmailNotificationLog.objects.all()
        else:
            # Users can only see their own logs
            return EmailNotificationLog.objects.filter(recipient=user)
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """Get current user's notification logs"""
        logs = EmailNotificationLog.objects.filter(recipient=request.user)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
