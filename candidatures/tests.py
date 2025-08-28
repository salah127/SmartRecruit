import tempfile
import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import Candidature

User = get_user_model()


class CandidatureTestCase(TestCase):
    """
    Test cases for candidature management with file upload
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.recruiter_user = User.objects.create_user(
            username='recruiter_test',
            email='recruiter@test.com',
            password='testpass123',
            role='recruteur'
        )
        
        self.candidate_user = User.objects.create_user(
            username='candidate_test',
            email='candidate@test.com',
            password='testpass123',
            role='candidat'
        )
        
        # Create test files
        self.cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        self.lettre_file = SimpleUploadedFile(
            "test_lettre.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
    
    def test_candidate_can_create_candidature(self):
        """Test that candidates can create candidatures"""
        self.client.force_authenticate(user=self.candidate_user)
        
        data = {
            'poste': 'Développeur Python',
            'cv': self.cv_file,
            'lettre_motivation': self.lettre_file,
            'message': 'Je suis très motivé pour ce poste.'
        }
        
        response = self.client.post('/api/candidatures/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Candidature.objects.count(), 1)
    
    def test_non_candidate_cannot_create_candidature(self):
        """Test that non-candidates cannot create candidatures"""
        self.client.force_authenticate(user=self.recruiter_user)
        
        data = {
            'poste': 'Développeur Python',
            'cv': self.cv_file,
            'message': 'Test message'
        }
        
        response = self.client.post('/api/candidatures/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_candidate_can_view_own_candidatures(self):
        """Test that candidates can view their own candidatures"""
        candidature = Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get('/api/candidatures/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_recruiter_can_view_all_candidatures(self):
        """Test that recruiters can view all candidatures"""
        candidature = Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get('/api/candidatures/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_recruiter_can_update_candidature_status(self):
        """Test that recruiters can update candidature status"""
        candidature = Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.post(
            f'/api/candidatures/{candidature.id}/update_status/',
            {'status': 'acceptee', 'commentaire': 'Excellent profil'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        candidature.refresh_from_db()
        self.assertEqual(candidature.status, 'acceptee')
    
    def test_candidate_cannot_update_status(self):
        """Test that candidates cannot update candidature status"""
        candidature = Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.post(
            f'/api/candidatures/{candidature.id}/update_status/',
            {'status': 'acceptee'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_delete_candidature(self):
        """Test that admins can delete candidatures"""
        candidature = Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/candidatures/{candidature.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Candidature.objects.count(), 0)
    
    def test_candidate_cannot_delete_candidature(self):
        """Test that candidates cannot delete candidatures"""
        candidature = Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.delete(f'/api/candidatures/{candidature.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unique_candidature_per_poste(self):
        """Test that a candidate can only apply once per position"""
        # Create first candidature
        Candidature.objects.create(
            candidat=self.candidate_user,
            poste='Test Position',
            cv=self.cv_file
        )
        
        self.client.force_authenticate(user=self.candidate_user)
        
        # Try to create second candidature for same position
        data = {
            'poste': 'Test Position',
            'cv': self.cv_file,
            'message': 'Second application'
        }
        
        response = self.client.post('/api/candidatures/', data, format='multipart')
        # Should fail due to unique constraint
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
