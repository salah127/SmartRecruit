from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from candidatures.models import Candidature
from .models import EmailPreferences, EmailNotificationLog
from .services import EmailNotificationService

User = get_user_model()


class EmailPreferencesTestCase(TestCase):
    """Test cases for email preferences functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_default_preferences_creation(self):
        """Test that default preferences are created"""
        preferences = EmailPreferences.objects.create(user=self.user)
        
        # Default values should be True
        self.assertTrue(preferences.receive_status_updates)
        self.assertTrue(preferences.receive_assignment_notifications)
        self.assertTrue(preferences.receive_new_candidature_alerts)


class EmailNotificationServiceTestCase(TestCase):
    """Test cases for email notification service"""
    
    def setUp(self):
        """Set up test data"""
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
        
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        self.candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Développeur Python',
            cv=cv_file,
            status='en_attente'
        )
        
        self.service = EmailNotificationService()
    
    @patch('notifications.services.send_mail')
    def test_send_candidature_status_update(self, mock_send_mail):
        """Test sending candidature status change notification"""
        mock_send_mail.return_value = True
        
        # Update status to trigger notification
        self.candidature.status = 'acceptee'
        self.candidature.save()
        
        result = self.service.send_candidature_status_update(self.candidature)
        
        # Should send email if preferences allow
        mock_send_mail.assert_called_once()


class EmailNotificationLogTestCase(TestCase):
    """Test cases for email notification logging"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_log_creation(self):
        """Test creating an email notification log"""
        log = EmailNotificationLog.objects.create(
            recipient=self.user,
            notification_type='candidature_status_update',
            subject='Test Subject',
            success=True
        )
        
        self.assertEqual(log.recipient, self.user)
        self.assertEqual(log.notification_type, 'candidature_status_update')
        self.assertTrue(log.success)


class NotificationIntegrationTestCase(TestCase):
    """Integration tests for notification system"""
    
    def setUp(self):
        """Set up test data"""
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_complete_notification_workflow(self):
        """Test complete notification workflow"""
        # Create candidature
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Full Stack Developer',
            cv=cv_file,
            status='en_attente'
        )
        
        # Check that candidature was created
        self.assertEqual(candidature.status, 'en_attente')
