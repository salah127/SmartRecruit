from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from candidatures.models import Candidature

User = get_user_model()


class CandidatureModelTestCase(TestCase):
    """Test cases for Candidature model"""
    
    def setUp(self):
        """Set up test data"""
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
        
        self.recruiter = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='testpass123',
            role='recruteur'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
    
    def test_candidature_creation(self):
        """Test creating a candidature"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Développeur Python',
            cv=cv_file,
            status='en_attente'
        )
        
        self.assertEqual(candidature.candidat, self.candidate)
        self.assertEqual(candidature.poste, 'Développeur Python')
        self.assertEqual(candidature.status, 'en_attente')
        self.assertIsNotNone(candidature.cv)
    
    def test_candidature_str_method(self):
        """Test string representation of candidature"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Développeur Python',
            cv=cv_file
        )
        
        expected = f"Candidature de {self.candidate.username} pour Développeur Python"
        self.assertEqual(str(candidature), expected)
    
    def test_status_choices(self):
        """Test candidature status choices"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Test Position',
            cv=cv_file
        )
        
        # Test different status values
        valid_statuses = ['en_attente', 'acceptee', 'refusee', 'en_cours']
        
        for status in valid_statuses:
            candidature.status = status
            candidature.save()
            candidature.refresh_from_db()
            self.assertEqual(candidature.status, status)
    
    def test_recruiter_assignment(self):
        """Test assigning a recruiter to candidature"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Test Position',
            cv=cv_file
        )
        
        # Initially no recruiter assigned
        self.assertIsNone(candidature.recruteur_assigne)
        
        # Assign recruiter
        candidature.recruteur_assigne = self.recruiter
        candidature.save()
        
        candidature.refresh_from_db()
        self.assertEqual(candidature.recruteur_assigne, self.recruiter)
    
    def test_candidature_ordering(self):
        """Test candidature ordering by creation date"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        # Create multiple candidatures
        candidature1 = Candidature.objects.create(
            candidat=self.candidate,
            poste='Position 1',
            cv=cv_file
        )
        
        candidature2 = Candidature.objects.create(
            candidat=self.candidate,
            poste='Position 2',
            cv=cv_file
        )
        
        # Should be ordered by creation date (newest first)
        candidatures = list(Candidature.objects.all())
        self.assertEqual(candidatures[0], candidature2)  # Newest first
        self.assertEqual(candidatures[1], candidature1)


class CandidaturePermissionsTestCase(TestCase):
    """Test cases for candidature permissions"""
    
    def setUp(self):
        """Set up test data"""
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
        
        self.recruiter = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='testpass123',
            role='recruteur'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
    
    def test_candidate_role_permissions(self):
        """Test candidate role permissions"""
        self.assertEqual(self.candidate.role, 'candidat')
        self.assertFalse(self.candidate.is_staff)
        self.assertFalse(self.candidate.is_superuser)
    
    def test_recruiter_role_permissions(self):
        """Test recruiter role permissions"""
        self.assertEqual(self.recruiter.role, 'recruteur')
        self.assertFalse(self.recruiter.is_staff)
        self.assertFalse(self.recruiter.is_superuser)
    
    def test_admin_role_permissions(self):
        """Test admin role permissions"""
        self.assertEqual(self.admin.role, 'admin')
        # Admin should have staff privileges if configured
        # self.assertTrue(self.admin.is_staff)


class CandidatureFileHandlingTestCase(TestCase):
    """Test cases for file handling in candidatures"""
    
    def setUp(self):
        """Set up test data"""
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_cv_file_upload(self):
        """Test CV file upload"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Test Position',
            cv=cv_file
        )
        
        self.assertIsNotNone(candidature.cv)
        self.assertTrue(candidature.cv.name.endswith('.pdf'))
    
    def test_lettre_motivation_upload(self):
        """Test lettre de motivation upload"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        lettre_file = SimpleUploadedFile(
            "lettre.pdf",
            b"fake lettre content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Test Position',
            cv=cv_file,
            lettre_motivation=lettre_file
        )
        
        self.assertIsNotNone(candidature.lettre_motivation)
        self.assertTrue(candidature.lettre_motivation.name.endswith('.pdf'))
    
    def test_file_paths_organization(self):
        """Test that files are organized properly"""
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Test Position',
            cv=cv_file
        )
        
        # File should be stored in candidatures/{user_id}/ directory
        self.assertIn(f'candidatures/{self.candidate.id}/', candidature.cv.name)


class CandidatureIntegrationTestCase(TestCase):
    """Integration tests for candidature functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
        
        self.recruiter = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='testpass123',
            role='recruteur'
        )
    
    def test_complete_candidature_workflow(self):
        """Test complete candidature workflow"""
        # 1. Candidate creates candidature
        cv_file = SimpleUploadedFile(
            "candidate_cv.pdf",
            b"candidate cv content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.candidate,
            poste='Full Stack Developer',
            cv=cv_file,
            message='I am very interested in this position.'
        )
        
        # Verify initial state
        self.assertEqual(candidature.status, 'en_attente')
        self.assertIsNone(candidature.recruteur_assigne)
        
        # 2. Recruiter gets assigned
        candidature.recruteur_assigne = self.recruiter
        candidature.save()
        
        candidature.refresh_from_db()
        self.assertEqual(candidature.recruteur_assigne, self.recruiter)
        
        # 3. Recruiter updates status
        candidature.status = 'en_cours'
        candidature.commentaire = 'Under review by technical team'
        candidature.save()
        
        candidature.refresh_from_db()
        self.assertEqual(candidature.status, 'en_cours')
        self.assertEqual(candidature.commentaire, 'Under review by technical team')
        
        # 4. Final decision
        candidature.status = 'acceptee'
        candidature.commentaire = 'Excellent candidate, offering position'
        candidature.save()
        
        candidature.refresh_from_db()
        self.assertEqual(candidature.status, 'acceptee')
        
        # Verify candidature exists and is complete
        self.assertTrue(Candidature.objects.filter(id=candidature.id).exists())
        self.assertEqual(candidature.candidat, self.candidate)
        self.assertEqual(candidature.recruteur_assigne, self.recruiter)
