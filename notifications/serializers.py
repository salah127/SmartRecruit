from rest_framework import serializers
from .models import EmailPreferences, EmailNotificationLog


class EmailPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPreferences
        fields = [
            'receive_status_updates',
            'receive_new_candidature_notifications',
            'receive_assignment_notifications',
            'updated_at'
        ]
        read_only_fields = ['updated_at']


class EmailNotificationLogSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    candidature_poste = serializers.CharField(source='candidature.poste', read_only=True)
    
    class Meta:
        model = EmailNotificationLog
        fields = [
            'id',
            'recipient_username',
            'notification_type',
            'notification_type_display',
            'subject',
            'candidature_poste',
            'sent_at',
            'success',
            'error_message'
        ]
