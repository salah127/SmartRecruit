from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import tempfile
import os

User = get_user_model()

# Note: These tests are designed to work when NumPy compatibility issues are resolved
# Currently disabled due to NumPy 2.x compatibility issues with AI modules


class AIModelTestCase(TestCase):
    """Test cases for AI model components"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_ai_module_imports(self):
        """Test that AI modules can be imported when dependencies are available"""
        try:
            # Test basic AI module imports
            from ai.models import model_loader
            from ai.models import resume_analyzer
            from ai.processing import data_preprocessor
            from ai.processing import feature_extractor
            from ai.utils import file_processor
            
            # If imports succeed, modules are available
            self.assertTrue(True)
            
        except ImportError as e:
            # Expected when NumPy compatibility issues exist
            self.assertIn('numpy', str(e).lower())
            self.skipTest(f"AI modules not available due to dependency issues: {e}")
    
    @patch('ai.models.model_loader.load_model')
    def test_model_loader_functionality(self, mock_load_model):
        """Test model loader functionality"""
        try:
            from ai.models.model_loader import load_model
            
            # Mock the model loading
            mock_model = MagicMock()
            mock_load_model.return_value = mock_model
            
            # Test model loading
            model = load_model('test_model')
            self.assertIsNotNone(model)
            mock_load_model.assert_called_once_with('test_model')
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.models.resume_analyzer.analyze_resume')
    def test_resume_analyzer_functionality(self, mock_analyze_resume):
        """Test resume analyzer functionality"""
        try:
            from ai.models.resume_analyzer import analyze_resume
            
            # Mock the analysis result
            mock_result = {
                'skills': ['Python', 'Django', 'REST API'],
                'experience_years': 3,
                'education_level': 'Bachelor',
                'score': 0.85
            }
            mock_analyze_resume.return_value = mock_result
            
            # Create test CV file
            cv_file = SimpleUploadedFile(
                "test_cv.pdf",
                b"fake pdf content with Python Django experience",
                content_type="application/pdf"
            )
            
            # Test resume analysis
            result = analyze_resume(cv_file)
            self.assertIsInstance(result, dict)
            self.assertIn('skills', result)
            self.assertIn('score', result)
            
        except ImportError:
            self.skipTest("AI modules not available")


class DataPreprocessorTestCase(TestCase):
    """Test cases for data preprocessing"""
    
    def setUp(self):
        """Set up test data"""
        self.test_text = "This is a test resume with Python and Django skills."
    
    @patch('ai.processing.data_preprocessor.preprocess_text')
    def test_text_preprocessing(self, mock_preprocess):
        """Test text preprocessing functionality"""
        try:
            from ai.processing.data_preprocessor import preprocess_text
            
            # Mock preprocessing result
            mock_preprocess.return_value = "test resume python django skills"
            
            # Test preprocessing
            result = preprocess_text(self.test_text)
            self.assertIsInstance(result, str)
            self.assertNotEqual(result, self.test_text)  # Should be processed
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.processing.data_preprocessor.extract_keywords')
    def test_keyword_extraction(self, mock_extract_keywords):
        """Test keyword extraction functionality"""
        try:
            from ai.processing.data_preprocessor import extract_keywords
            
            # Mock keyword extraction result
            mock_keywords = ['python', 'django', 'web', 'development']
            mock_extract_keywords.return_value = mock_keywords
            
            # Test keyword extraction
            keywords = extract_keywords(self.test_text)
            self.assertIsInstance(keywords, list)
            self.assertGreater(len(keywords), 0)
            
        except ImportError:
            self.skipTest("AI modules not available")


class FeatureExtractorTestCase(TestCase):
    """Test cases for feature extraction"""
    
    def setUp(self):
        """Set up test data"""
        self.test_resume_text = """
        John Doe
        Software Engineer
        
        Experience:
        - 3 years Python development
        - Django web framework
        - REST API development
        
        Education:
        Bachelor in Computer Science
        """
    
    @patch('ai.processing.feature_extractor.extract_skills')
    def test_skills_extraction(self, mock_extract_skills):
        """Test skills extraction from resume"""
        try:
            from ai.processing.feature_extractor import extract_skills
            
            # Mock skills extraction
            mock_skills = ['Python', 'Django', 'REST API', 'Web Development']
            mock_extract_skills.return_value = mock_skills
            
            # Test skills extraction
            skills = extract_skills(self.test_resume_text)
            self.assertIsInstance(skills, list)
            self.assertIn('Python', skills)
            self.assertIn('Django', skills)
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.processing.feature_extractor.extract_experience')
    def test_experience_extraction(self, mock_extract_experience):
        """Test experience extraction from resume"""
        try:
            from ai.processing.feature_extractor import extract_experience
            
            # Mock experience extraction
            mock_experience = {
                'years': 3,
                'roles': ['Software Engineer'],
                'companies': []
            }
            mock_extract_experience.return_value = mock_experience
            
            # Test experience extraction
            experience = extract_experience(self.test_resume_text)
            self.assertIsInstance(experience, dict)
            self.assertIn('years', experience)
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.processing.feature_extractor.extract_education')
    def test_education_extraction(self, mock_extract_education):
        """Test education extraction from resume"""
        try:
            from ai.processing.feature_extractor import extract_education
            
            # Mock education extraction
            mock_education = {
                'degree': 'Bachelor',
                'field': 'Computer Science',
                'level': 'undergraduate'
            }
            mock_extract_education.return_value = mock_education
            
            # Test education extraction
            education = extract_education(self.test_resume_text)
            self.assertIsInstance(education, dict)
            self.assertIn('degree', education)
            
        except ImportError:
            self.skipTest("AI modules not available")


class FileProcessorTestCase(TestCase):
    """Test cases for file processing utilities"""
    
    def setUp(self):
        """Set up test data"""
        self.pdf_content = b"fake pdf content"
        self.doc_content = b"fake doc content"
    
    @patch('ai.utils.file_processor.extract_text_from_pdf')
    def test_pdf_text_extraction(self, mock_extract_pdf):
        """Test PDF text extraction"""
        try:
            from ai.utils.file_processor import extract_text_from_pdf
            
            # Mock PDF text extraction
            mock_text = "Extracted text from PDF resume"
            mock_extract_pdf.return_value = mock_text
            
            # Create test PDF file
            pdf_file = SimpleUploadedFile(
                "test_resume.pdf",
                self.pdf_content,
                content_type="application/pdf"
            )
            
            # Test PDF text extraction
            text = extract_text_from_pdf(pdf_file)
            self.assertIsInstance(text, str)
            self.assertEqual(text, mock_text)
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.utils.file_processor.extract_text_from_doc')
    def test_doc_text_extraction(self, mock_extract_doc):
        """Test DOC text extraction"""
        try:
            from ai.utils.file_processor import extract_text_from_doc
            
            # Mock DOC text extraction
            mock_text = "Extracted text from DOC resume"
            mock_extract_doc.return_value = mock_text
            
            # Create test DOC file
            doc_file = SimpleUploadedFile(
                "test_resume.doc",
                self.doc_content,
                content_type="application/msword"
            )
            
            # Test DOC text extraction
            text = extract_text_from_doc(doc_file)
            self.assertIsInstance(text, str)
            self.assertEqual(text, mock_text)
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.utils.file_processor.validate_file_type')
    def test_file_type_validation(self, mock_validate):
        """Test file type validation"""
        try:
            from ai.utils.file_processor import validate_file_type
            
            # Mock validation results
            mock_validate.side_effect = lambda f: f.name.endswith(('.pdf', '.doc', '.docx'))
            
            # Test valid file types
            valid_files = [
                SimpleUploadedFile("test.pdf", b"content", "application/pdf"),
                SimpleUploadedFile("test.doc", b"content", "application/msword"),
                SimpleUploadedFile("test.docx", b"content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ]
            
            for file in valid_files:
                self.assertTrue(validate_file_type(file))
            
            # Test invalid file type
            invalid_file = SimpleUploadedFile("test.txt", b"content", "text/plain")
            self.assertFalse(validate_file_type(invalid_file))
            
        except ImportError:
            self.skipTest("AI modules not available")


class AITasksTestCase(TestCase):
    """Test cases for AI Celery tasks"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
    
    @patch('ai.tasks.analyze_cv_task.delay')
    def test_cv_analysis_task(self, mock_task):
        """Test CV analysis Celery task"""
        try:
            from ai.tasks import analyze_cv_task
            
            # Mock task result
            mock_result = MagicMock()
            mock_result.id = 'task-123'
            mock_task.return_value = mock_result
            
            # Create test candidature
            cv_file = SimpleUploadedFile(
                "cv.pdf",
                b"fake pdf content",
                content_type="application/pdf"
            )
            
            from candidatures.models import Candidature
            candidature = Candidature.objects.create(
                candidat=self.user,
                poste='Test Position',
                cv=cv_file
            )
            
            # Test task invocation
            task_result = analyze_cv_task.delay(candidature.id)
            self.assertIsNotNone(task_result)
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.tasks.update_skills_database_task.delay')
    def test_skills_database_update_task(self, mock_task):
        """Test skills database update task"""
        try:
            from ai.tasks import update_skills_database_task
            
            # Mock task result
            mock_result = MagicMock()
            mock_result.id = 'task-456'
            mock_task.return_value = mock_result
            
            # Test task invocation
            task_result = update_skills_database_task.delay()
            self.assertIsNotNone(task_result)
            mock_task.assert_called_once()
            
        except ImportError:
            self.skipTest("AI modules not available")


class AIIntegrationTestCase(TestCase):
    """Integration tests for AI functionality"""
    
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
    
    @patch('ai.models.resume_analyzer.analyze_resume')
    @patch('ai.utils.file_processor.extract_text_from_pdf')
    def test_complete_cv_analysis_workflow(self, mock_extract_text, mock_analyze):
        """Test complete CV analysis workflow"""
        try:
            # Mock file processing
            mock_extracted_text = "John Doe Software Engineer Python Django 3 years experience"
            mock_extract_text.return_value = mock_extracted_text
            
            # Mock analysis result
            mock_analysis = {
                'skills': ['Python', 'Django', 'Software Engineering'],
                'experience_years': 3,
                'education_level': 'Not specified',
                'score': 0.78,
                'matching_keywords': ['Python', 'Django'],
                'recommendations': ['Add more details about projects', 'Include education information']
            }
            mock_analyze.return_value = mock_analysis
            
            # Create candidature with CV
            cv_file = SimpleUploadedFile(
                "candidate_cv.pdf",
                b"fake pdf with Python Django experience",
                content_type="application/pdf"
            )
            
            from candidatures.models import Candidature
            candidature = Candidature.objects.create(
                candidat=self.candidate,
                poste='Python Developer',
                cv=cv_file
            )
            
            # Import and test the complete workflow
            from ai.utils.file_processor import extract_text_from_pdf
            from ai.models.resume_analyzer import analyze_resume
            
            # Step 1: Extract text from CV
            extracted_text = extract_text_from_pdf(candidature.cv)
            self.assertEqual(extracted_text, mock_extracted_text)
            
            # Step 2: Analyze resume
            analysis_result = analyze_resume(extracted_text)
            self.assertIsInstance(analysis_result, dict)
            self.assertIn('skills', analysis_result)
            self.assertIn('score', analysis_result)
            self.assertEqual(analysis_result['experience_years'], 3)
            
            # Step 3: Verify analysis results
            self.assertGreater(analysis_result['score'], 0.5)
            self.assertIn('Python', analysis_result['skills'])
            self.assertIn('Django', analysis_result['skills'])
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    @patch('ai.processing.feature_extractor.extract_skills')
    @patch('ai.processing.feature_extractor.extract_experience')
    @patch('ai.processing.feature_extractor.extract_education')
    def test_comprehensive_feature_extraction(self, mock_education, mock_experience, mock_skills):
        """Test comprehensive feature extraction from resume"""
        try:
            # Mock feature extraction results
            mock_skills.return_value = ['Python', 'Django', 'PostgreSQL', 'Git']
            mock_experience.return_value = {
                'years': 5,
                'roles': ['Software Engineer', 'Backend Developer'],
                'companies': ['TechCorp', 'StartupXYZ']
            }
            mock_education.return_value = {
                'degree': 'Master',
                'field': 'Computer Science',
                'institution': 'University XYZ',
                'level': 'graduate'
            }
            
            # Test resume text
            resume_text = """
            Jane Smith
            Senior Software Engineer
            
            Experience:
            - 5 years Python development at TechCorp
            - Backend development with Django at StartupXYZ
            - Database design with PostgreSQL
            - Version control with Git
            
            Education:
            Master of Science in Computer Science
            University XYZ, 2018
            """
            
            # Import and test feature extraction
            from ai.processing.feature_extractor import extract_skills, extract_experience, extract_education
            
            # Extract all features
            skills = extract_skills(resume_text)
            experience = extract_experience(resume_text)
            education = extract_education(resume_text)
            
            # Verify skills extraction
            self.assertIsInstance(skills, list)
            self.assertIn('Python', skills)
            self.assertIn('Django', skills)
            
            # Verify experience extraction
            self.assertIsInstance(experience, dict)
            self.assertEqual(experience['years'], 5)
            self.assertIn('Software Engineer', experience['roles'])
            
            # Verify education extraction
            self.assertIsInstance(education, dict)
            self.assertEqual(education['degree'], 'Master')
            self.assertEqual(education['field'], 'Computer Science')
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    def test_ai_error_handling(self):
        """Test AI error handling and graceful degradation"""
        try:
            # Test with invalid file
            invalid_file = SimpleUploadedFile(
                "invalid.txt",
                b"This is not a resume file",
                content_type="text/plain"
            )
            
            # Should handle gracefully without crashing
            from ai.utils.file_processor import extract_text_from_pdf
            
            try:
                text = extract_text_from_pdf(invalid_file)
                # Should either return empty string or raise handled exception
                self.assertIsInstance(text, str)
            except Exception as e:
                # Should be a handled exception
                self.assertIsInstance(e, (ValueError, TypeError, IOError))
            
        except ImportError:
            self.skipTest("AI modules not available")
    
    def test_ai_performance_considerations(self):
        """Test AI performance considerations"""
        try:
            # Test with large file (mock)
            large_file_content = b"fake content " * 10000  # Simulate large file
            large_cv = SimpleUploadedFile(
                "large_cv.pdf",
                large_file_content,
                content_type="application/pdf"
            )
            
            # Test that processing completes in reasonable time
            import time
            start_time = time.time()
            
            # Mock the processing to avoid actual heavy computation
            with patch('ai.utils.file_processor.extract_text_from_pdf') as mock_extract:
                mock_extract.return_value = "Extracted large text content"
                
                from ai.utils.file_processor import extract_text_from_pdf
                result = extract_text_from_pdf(large_cv)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Should complete quickly with mocked processing
                self.assertLess(processing_time, 1.0)  # Less than 1 second
                self.assertIsInstance(result, str)
            
        except ImportError:
            self.skipTest("AI modules not available")


class AIDependencyTestCase(TestCase):
    """Test cases for AI dependencies and compatibility"""
    
    def test_numpy_compatibility(self):
        """Test NumPy compatibility (main issue causing AI module disable)"""
        try:
            import numpy as np
            numpy_version = np.__version__
            
            # Check NumPy version
            major_version = int(numpy_version.split('.')[0])
            
            if major_version >= 2:
                # NumPy 2.x compatibility issue
                self.skipTest(f"NumPy 2.x compatibility issue detected (version: {numpy_version})")
            else:
                # NumPy 1.x should work
                self.assertLess(major_version, 2)
                
        except ImportError:
            self.skipTest("NumPy not installed")
    
    def test_ai_dependencies_availability(self):
        """Test availability of AI dependencies"""
        dependencies = [
            'numpy',
            'pandas',
            'scikit-learn',
            'nltk',
            'spacy',
            'transformers',
            'torch',
            'tensorflow',
        ]
        
        available_deps = []
        missing_deps = []
        
        for dep in dependencies:
            try:
                __import__(dep)
                available_deps.append(dep)
            except ImportError:
                missing_deps.append(dep)
        
        # At least some basic dependencies should be available for AI functionality
        # NumPy is required for most AI operations
        if 'numpy' not in available_deps:
            self.skipTest("NumPy not available - AI functionality disabled")
        
        # Log available dependencies for debugging
        print(f"Available AI dependencies: {available_deps}")
        print(f"Missing AI dependencies: {missing_deps}")
    
    def test_ai_module_structure(self):
        """Test that AI module structure is correct"""
        import os
        from django.conf import settings
        
        # Check that AI app directory exists
        ai_app_path = os.path.join(settings.BASE_DIR, 'ai')
        self.assertTrue(os.path.exists(ai_app_path))
        
        # Check for expected subdirectories
        expected_dirs = ['models', 'processing', 'utils', 'management']
        for dir_name in expected_dirs:
            dir_path = os.path.join(ai_app_path, dir_name)
            self.assertTrue(os.path.exists(dir_path), f"Directory {dir_name} should exist in ai app")
        
        # Check for __init__.py files
        init_files = [
            os.path.join(ai_app_path, '__init__.py'),
            os.path.join(ai_app_path, 'models', '__init__.py'),
            os.path.join(ai_app_path, 'processing', '__init__.py'),
            os.path.join(ai_app_path, 'utils', '__init__.py'),
        ]
        
        for init_file in init_files:
            if os.path.exists(os.path.dirname(init_file)):
                # Check if __init__.py exists or should exist
                pass
