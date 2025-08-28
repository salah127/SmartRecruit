from django.contrib import admin
from .models import EmailPreferences, EmailNotificationLog


@admin.register(EmailPreferences)
class EmailPreferencesAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'receive_status_updates',
        'receive_new_candidature_notifications', 
        'receive_assignment_notifications',
        'updated_at'
    ]
    list_filter = [
        'receive_status_updates',
        'receive_new_candidature_notifications', 
        'receive_assignment_notifications',
        'user__role'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailNotificationLog)
class EmailNotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'recipient',
        'notification_type', 
        'subject',
        'candidature',
        'success',
        'sent_at'
    ]
    list_filter = [
        'notification_type',
        'success',
        'sent_at',
        'recipient__role'
    ]
    search_fields = [
        'recipient__username',
        'recipient__email', 
        'subject',
        'candidature__poste'
    ]
    readonly_fields = ['sent_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
