from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from candidatures.models import Candidature
from .services import EmailNotificationService


@receiver(post_save, sender=Candidature)
def handle_candidature_created(sender, instance, created, **kwargs):
    """Handle new candidature creation"""
    if created:
        # Send notification to recruiters about new candidature
        EmailNotificationService.send_new_candidature_notification(instance)


@receiver(pre_save, sender=Candidature)
def handle_candidature_status_change(sender, instance, **kwargs):
    """Handle candidature status changes"""
    if instance.pk:  # Instance already exists
        try:
            old_instance = Candidature.objects.get(pk=instance.pk)
            
            # Check if status changed
            if old_instance.status != instance.status and instance.status != 'en_attente':
                # Store flag to send notification after save
                instance._status_changed = True
                instance._old_status = old_instance.status
                
            # Check if recruiter assignment changed
            if old_instance.recruteur_assigne != instance.recruteur_assigne and instance.recruteur_assigne:
                instance._recruiter_assigned = True
                
        except Candidature.DoesNotExist:
            pass


@receiver(post_save, sender=Candidature)
def handle_candidature_updated(sender, instance, created, **kwargs):
    """Handle candidature updates"""
    if not created:
        # Send status update notification if status changed
        if hasattr(instance, '_status_changed') and instance._status_changed:
            EmailNotificationService.send_candidature_status_update(instance)
            delattr(instance, '_status_changed')
            if hasattr(instance, '_old_status'):
                delattr(instance, '_old_status')
        
        # Send recruiter assignment notification
        if hasattr(instance, '_recruiter_assigned') and instance._recruiter_assigned:
            EmailNotificationService.send_recruiter_assignment_notification(instance)
            delattr(instance, '_recruiter_assigned')
