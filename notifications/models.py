from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailPreferences(models.Model):
    """Model to manage user email notification preferences"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_preferences'
    )
    
    # Notification preferences
    receive_status_updates = models.BooleanField(
        default=True,
        verbose_name='Recevoir les mises à jour de statut'
    )
    
    receive_new_candidature_notifications = models.BooleanField(
        default=True,
        verbose_name='Recevoir les notifications de nouvelles candidatures'
    )
    
    receive_assignment_notifications = models.BooleanField(
        default=True,
        verbose_name='Recevoir les notifications d\'assignation'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Préférences email'
        verbose_name_plural = 'Préférences email'
    
    def __str__(self):
        return f"Préférences email - {self.user.username}"


class EmailNotificationLog(models.Model):
    """Model to log sent email notifications for tracking purposes"""
    
    NOTIFICATION_TYPES = [
        ('status_update', 'Mise à jour de statut'),
        ('new_candidature', 'Nouvelle candidature'),
        ('recruiter_assignment', 'Assignation recruteur'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    
    subject = models.CharField(max_length=255)
    
    candidature = models.ForeignKey(
        'candidatures.Candidature',
        on_delete=models.CASCADE,
        related_name='email_notifications',
        null=True,
        blank=True
    )
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    success = models.BooleanField(default=True)
    
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Log de notification'
        verbose_name_plural = 'Logs de notifications'
        ordering = ['-sent_at']
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.get_notification_type_display()} - {self.recipient.username}"
