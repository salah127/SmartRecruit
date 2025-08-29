from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from candidatures.models import Candidature
from .tasks import analyze_cv_async
from .processing.data_preprocessor import CVPreprocessor
from .processing.feature_extractor import FeatureExtractor
from .models.resume_analyzer import ResumeAnalyzer

User = get_user_model()


class CVPreprocessorTestCase(TestCase):
    """Test cases for CV preprocessing functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.preprocessor = CVPreprocessor()
        
        # Create test PDF content
        self.test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000074 00000 n\n0000000120 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n178\n%%EOF"
    
    @patch('ai.processing.data_preprocessor.extract_text')
    def test_extract_text_from_pdf(self, mock_extract_text):
        """Test text extraction from PDF files"""
        mock_extract_text.return_value = "John Doe\nSoftware Engineer\nPython, Django, JavaScript"
        
        cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        result = self.preprocessor.extract_text_from_file(cv_file)
        
        self.assertIsInstance(result, str)
        self.assertIn("John Doe", result)
        mock_extract_text.assert_called_once()
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        raw_text = "  John  Doe\n\n  Software Engineer  \n\n\nSkills: Python, Django  "
        
        cleaned_text = self.preprocessor.clean_text(raw_text)
        
        self.assertNotIn("  ", cleaned_text)  # No double spaces
        self.assertNotIn("\n\n", cleaned_text)  # No double newlines
        self.assertEqual(cleaned_text.strip(), cleaned_text)  # No leading/trailing spaces
    
    @patch('ai.processing.data_preprocessor.spacy.load')
    def test_tokenize_text(self, mock_spacy_load):
        """Test text tokenization"""
        # Mock spaCy nlp object
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_token1 = MagicMock()
        mock_token1.text = "Python"
        mock_token1.is_alpha = True
        mock_token1.is_stop = False
        
        mock_token2 = MagicMock()
        mock_token2.text = "the"
        mock_token2.is_alpha = True
        mock_token2.is_stop = True
        
        mock_doc.__iter__ = lambda x: iter([mock_token1, mock_token2])
        mock_nlp.return_value = mock_doc
        mock_spacy_load.return_value = mock_nlp
        
        text = "Python is the best programming language"
        tokens = self.preprocessor.tokenize_text(text)
        
        # Should filter out stop words
        self.assertIn("Python", tokens)
        self.assertNotIn("the", tokens)
    
    def test_extract_skills(self):
        """Test skill extraction from text"""
        text = "I have experience with Python, Django, JavaScript, React, SQL databases"
        
        skills = self.preprocessor.extract_skills(text)
        
        self.assertIsInstance(skills, list)
        # Should extract at least some programming skills
        expected_skills = ["Python", "Django", "JavaScript"]
        for skill in expected_skills:
            self.assertIn(skill.lower(), [s.lower() for s in skills])
    
    def test_extract_education(self):
        """Test education extraction from text"""
        text = "Master's degree in Computer Science from MIT. Bachelor in Software Engineering."
        
        education = self.preprocessor.extract_education(text)
        
        self.assertIsInstance(education, list)
        # Should extract education information
        education_text = " ".join(education).lower()
        self.assertIn("master", education_text)
        self.assertIn("computer science", education_text)


class FeatureExtractorTestCase(TestCase):
    """Test cases for feature extraction functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.extractor = FeatureExtractor()
    
    def test_extract_experience_years(self):
        """Test experience years extraction"""
        text_5_years = "I have 5 years of experience in software development"
        text_no_exp = "Recent graduate seeking opportunities"
        
        exp_5 = self.extractor.extract_experience_years(text_5_years)
        exp_0 = self.extractor.extract_experience_years(text_no_exp)
        
        self.assertEqual(exp_5, 5)
        self.assertEqual(exp_0, 0)
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        text = "John Doe, email: john.doe@example.com, phone: +33 1 23 45 67 89"
        
        contact_info = self.extractor.extract_contact_info(text)
        
        self.assertIn("email", contact_info)
        self.assertIn("phone", contact_info)
        self.assertEqual(contact_info["email"], "john.doe@example.com")
    
    def test_calculate_skill_match_score(self):
        """Test skill matching score calculation"""
        cv_skills = ["Python", "Django", "JavaScript", "React"]
        job_requirements = ["Python", "Django", "PostgreSQL", "Docker"]
        
        score = self.extractor.calculate_skill_match_score(cv_skills, job_requirements)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        # Should have some match (Python, Django)
        self.assertGreater(score, 0.3)
    
    def test_extract_language_skills(self):
        """Test language skills extraction"""
        text = "Fluent in English and French. Basic Spanish. Native French speaker."
        
        languages = self.extractor.extract_language_skills(text)
        
        self.assertIsInstance(languages, list)
        language_text = " ".join(languages).lower()
        self.assertIn("english", language_text)
        self.assertIn("french", language_text)


class ResumeAnalyzerTestCase(TestCase):
    """Test cases for resume analysis functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.analyzer = ResumeAnalyzer()
    
    @patch('ai.models.resume_analyzer.joblib.load')
    def test_load_model(self, mock_joblib_load):
        """Test model loading"""
        mock_model = MagicMock()
        mock_joblib_load.return_value = mock_model
        
        model = self.analyzer.load_model()
        
        self.assertIsNotNone(model)
        mock_joblib_load.assert_called_once()
    
    @patch('ai.models.resume_analyzer.ResumeAnalyzer.load_model')
    def test_predict_suitability(self, mock_load_model):
        """Test suitability prediction"""
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [[0.3, 0.7]]  # 70% suitability
        mock_load_model.return_value = mock_model
        
        features = {
            'experience_years': 5,
            'skill_match_score': 0.8,
            'education_level': 3,
            'language_count': 2
        }
        
        suitability = self.analyzer.predict_suitability(features)
        
        self.assertGreaterEqual(suitability, 0.0)
        self.assertLessEqual(suitability, 1.0)
        self.assertAlmostEqual(suitability, 0.7, places=2)
    
    def test_analyze_resume_structure(self):
        """Test resume structure analysis"""
        cv_text = """
        John Doe
        Software Engineer
        
        Experience:
        - 5 years at TechCorp
        
        Education:
        - Master's in Computer Science
        
        Skills:
        - Python, Django, JavaScript
        """
        
        analysis = self.analyzer.analyze_resume_structure(cv_text)
        
        self.assertIn("has_experience_section", analysis)
        self.assertIn("has_education_section", analysis)
        self.assertIn("has_skills_section", analysis)
        self.assertTrue(analysis["has_experience_section"])
        self.assertTrue(analysis["has_education_section"])
        self.assertTrue(analysis["has_skills_section"])


class CVAnalysisTaskTestCase(TestCase):
    """Test cases for CV analysis Celery tasks"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='test_candidate',
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
            candidat=self.user,
            poste='Software Engineer',
            cv=cv_file
        )
    
    @patch('ai.tasks.CVPreprocessor')
    @patch('ai.tasks.FeatureExtractor')
    @patch('ai.tasks.ResumeAnalyzer')
    def test_analyze_cv_async_task(self, mock_analyzer, mock_extractor, mock_preprocessor):
        """Test asynchronous CV analysis task"""
        # Mock the components
        mock_preprocessor_instance = MagicMock()
        mock_preprocessor_instance.extract_text_from_file.return_value = "John Doe Software Engineer"
        mock_preprocessor_instance.extract_skills.return_value = ["Python", "Django"]
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_extractor_instance = MagicMock()
        mock_extractor_instance.extract_experience_years.return_value = 5
        mock_extractor_instance.calculate_skill_match_score.return_value = 0.8
        mock_extractor.return_value = mock_extractor_instance
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.predict_suitability.return_value = 0.85
        mock_analyzer_instance.analyze_resume_structure.return_value = {
            "has_experience_section": True,
            "has_education_section": True,
            "has_skills_section": True
        }
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Run the task
        result = analyze_cv_async(self.candidature.id)
        
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertIn("suitability_score", result)
        self.assertIn("extracted_skills", result)
        self.assertIn("experience_years", result)
        self.assertIn("analysis_date", result)
    
    def test_analyze_cv_with_invalid_candidature(self):
        """Test CV analysis with invalid candidature ID"""
        with self.assertRaises(Exception):
            analyze_cv_async(99999)  # Non-existent candidature ID


class AIIntegrationTestCase(TestCase):
    """Integration tests for AI functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
    
    @patch('ai.processing.data_preprocessor.extract_text')
    @patch('ai.models.resume_analyzer.joblib.load')
    def test_complete_cv_analysis_pipeline(self, mock_joblib_load, mock_extract_text):
        """Test the complete CV analysis pipeline"""
        # Mock text extraction
        mock_extract_text.return_value = """
        John Doe
        Senior Software Engineer
        
        Experience:
        - 5 years experience in Python development
        - Worked with Django, Flask, FastAPI
        - Experience with PostgreSQL, Redis
        
        Education:
        - Master's degree in Computer Science
        
        Skills:
        - Python, Django, JavaScript, React
        - PostgreSQL, Redis, Docker
        - Git, CI/CD
        """
        
        # Mock ML model
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [[0.2, 0.8]]
        mock_joblib_load.return_value = mock_model
        
        # Create candidature with CV
        cv_file = SimpleUploadedFile(
            "john_doe_cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        candidature = Candidature.objects.create(
            candidat=self.user,
            poste='Senior Python Developer',
            cv=cv_file
        )
        
        # Run analysis
        result = analyze_cv_async(candidature.id)
        
        # Verify results
        self.assertIsInstance(result, dict)
        self.assertIn("suitability_score", result)
        self.assertIn("extracted_skills", result)
        self.assertIn("experience_years", result)
        
        # Check that extracted data makes sense
        self.assertGreater(result["experience_years"], 0)
        self.assertGreater(len(result["extracted_skills"]), 0)
        self.assertGreaterEqual(result["suitability_score"], 0.0)
        self.assertLessEqual(result["suitability_score"], 1.0)
    
    def test_error_handling_in_analysis(self):
        """Test error handling in CV analysis"""
        # Create candidature with invalid CV
        candidature = Candidature.objects.create(
            candidat=self.user,
            poste='Test Position'
            # No CV file
        )
        
        # Should handle gracefully
        with patch('ai.tasks.logger') as mock_logger:
            try:
                result = analyze_cv_async(candidature.id)
                # Should either return error info or raise handled exception
            except Exception:
                # Error should be logged
                mock_logger.error.assert_called()
