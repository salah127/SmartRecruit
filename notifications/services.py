from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import EmailPreferences, EmailNotificationLog
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for sending email notifications"""
    
    @staticmethod
    def _get_or_create_preferences(user):
        """Get or create email preferences for a user"""
        preferences, created = EmailPreferences.objects.get_or_create(user=user)
        return preferences
    
    @staticmethod
    def _log_notification(recipient, notification_type, subject, candidature=None, success=True, error_message=None):
        """Log email notification"""
        EmailNotificationLog.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            subject=subject,
            candidature=candidature,
            success=success,
            error_message=error_message
        )
    
    @staticmethod
    def send_candidature_status_update(candidature):
        """Send email to candidate when candidature status is updated"""
        try:
            # Check user preferences
            preferences = EmailNotificationService._get_or_create_preferences(candidature.candidat)
            if not preferences.receive_status_updates:
                logger.info(f"Status update email skipped for {candidature.candidat.email} - user preferences")
                return
            
            subject = f"Mise à jour de votre candidature - {candidature.poste}"
            
            # Determine email template based on status
            if candidature.status == 'acceptee':
                template = 'emails/candidature_accepted.html'
            elif candidature.status == 'refusee':
                template = 'emails/candidature_rejected.html'
            elif candidature.status == 'en_cours':
                template = 'emails/candidature_in_progress.html'
            else:
                template = 'emails/candidature_status_update.html'
            
            context = {
                'candidature': candidature,
                'candidat': candidature.candidat,
                'status_display': candidature.get_status_display(),
            }
            
            html_message = render_to_string(template, context)
            plain_message = render_to_string('emails/candidature_status_update.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[candidature.candidat.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Log successful notification
            EmailNotificationService._log_notification(
                recipient=candidature.candidat,
                notification_type='status_update',
                subject=subject,
                candidature=candidature,
                success=True
            )
            
            logger.info(f"Status update email sent to {candidature.candidat.email} for candidature {candidature.id}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send status update email: {error_msg}")
            
            # Log failed notification
            try:
                EmailNotificationService._log_notification(
                    recipient=candidature.candidat,
                    notification_type='status_update',
                    subject=subject,
                    candidature=candidature,
                    success=False,
                    error_message=error_msg
                )
            except:
                pass
    
    @staticmethod
    def send_new_candidature_notification(candidature):
        """Send email to recruiters when a new candidature is received"""
        try:
            # Get all recruiters and admins
            recruiters = User.objects.filter(role__in=['recruteur', 'admin'])
            
            if not recruiters.exists():
                logger.warning("No recruiters found to notify about new candidature")
                return
            
            subject = f"Nouvelle candidature reçue - {candidature.poste}"
            
            context = {
                'candidature': candidature,
                'candidat': candidature.candidat,
                'poste': candidature.poste,
            }
            
            html_message = render_to_string('emails/new_candidature_notification.html', context)
            plain_message = render_to_string('emails/new_candidature_notification.txt', context)
            
            # Send to recruiters who want to receive notifications
            sent_count = 0
            for recruiter in recruiters:
                if not recruiter.email:
                    continue
                    
                preferences = EmailNotificationService._get_or_create_preferences(recruiter)
                if not preferences.receive_new_candidature_notifications:
                    continue
                
                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recruiter.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    # Log successful notification
                    EmailNotificationService._log_notification(
                        recipient=recruiter,
                        notification_type='new_candidature',
                        subject=subject,
                        candidature=candidature,
                        success=True
                    )
                    
                    sent_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to send new candidature notification to {recruiter.email}: {error_msg}")
                    
                    # Log failed notification
                    try:
                        EmailNotificationService._log_notification(
                            recipient=recruiter,
                            notification_type='new_candidature',
                            subject=subject,
                            candidature=candidature,
                            success=False,
                            error_message=error_msg
                        )
                    except:
                        pass
            
            logger.info(f"New candidature notification sent to {sent_count} recruiters")
                
        except Exception as e:
            logger.error(f"Failed to send new candidature notification: {str(e)}")
    
    @staticmethod
    def send_recruiter_assignment_notification(candidature):
        """Send email to recruiter when assigned to a candidature"""
        try:
            if not candidature.recruteur_assigne or not candidature.recruteur_assigne.email:
                return
            
            # Check user preferences
            preferences = EmailNotificationService._get_or_create_preferences(candidature.recruteur_assigne)
            if not preferences.receive_assignment_notifications:
                logger.info(f"Assignment notification skipped for {candidature.recruteur_assigne.email} - user preferences")
                return
            
            subject = f"Candidature assignée - {candidature.poste}"
            
            context = {
                'candidature': candidature,
                'candidat': candidature.candidat,
                'recruteur': candidature.recruteur_assigne,
            }
            
            html_message = render_to_string('emails/recruiter_assignment.html', context)
            plain_message = render_to_string('emails/recruiter_assignment.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[candidature.recruteur_assigne.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Log successful notification
            EmailNotificationService._log_notification(
                recipient=candidature.recruteur_assigne,
                notification_type='recruiter_assignment',
                subject=subject,
                candidature=candidature,
                success=True
            )
            
            logger.info(f"Assignment notification sent to {candidature.recruteur_assigne.email}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send assignment notification: {error_msg}")
            
            # Log failed notification
            try:
                EmailNotificationService._log_notification(
                    recipient=candidature.recruteur_assigne,
                    notification_type='recruiter_assignment',
                    subject=subject,
                    candidature=candidature,
                    success=False,
                    error_message=error_msg
                )
            except:
                pass
