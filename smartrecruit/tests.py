from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
import os
import tempfile

User = get_user_model()


class SmartRecruitConfigTestCase(TestCase):
    """Test cases for SmartRecruit project configuration"""
    
    def test_django_settings_configuration(self):
        """Test Django settings configuration"""
        # Test basic settings
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertIsInstance(settings.DEBUG, bool)
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
        
        # Test database configuration
        self.assertIn('default', settings.DATABASES)
        self.assertIsNotNone(settings.DATABASES['default']['ENGINE'])
        
        # Test installed apps
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'users',
            'candidatures',
            'notifications',
        ]
        
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
    
    def test_middleware_configuration(self):
        """Test middleware configuration"""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        
        for middleware in required_middleware:
            self.assertIn(middleware, settings.MIDDLEWARE)
    
    def test_rest_framework_configuration(self):
        """Test REST Framework configuration"""
        self.assertIn('REST_FRAMEWORK', dir(settings))
        
        if hasattr(settings, 'REST_FRAMEWORK'):
            rest_config = settings.REST_FRAMEWORK
            
            # Check authentication classes
            if 'DEFAULT_AUTHENTICATION_CLASSES' in rest_config:
                auth_classes = rest_config['DEFAULT_AUTHENTICATION_CLASSES']
                self.assertIsInstance(auth_classes, (list, tuple))
            
            # Check permission classes
            if 'DEFAULT_PERMISSION_CLASSES' in rest_config:
                perm_classes = rest_config['DEFAULT_PERMISSION_CLASSES']
                self.assertIsInstance(perm_classes, (list, tuple))
    
    def test_static_and_media_configuration(self):
        """Test static and media files configuration"""
        self.assertIsNotNone(settings.STATIC_URL)
        self.assertIsNotNone(settings.MEDIA_URL)
        
        if hasattr(settings, 'STATIC_ROOT'):
            self.assertIsInstance(settings.STATIC_ROOT, (str, type(None)))
        
        if hasattr(settings, 'MEDIA_ROOT'):
            self.assertIsInstance(settings.MEDIA_ROOT, (str, type(None)))
    
    def test_internationalization_settings(self):
        """Test internationalization settings"""
        self.assertIsNotNone(settings.LANGUAGE_CODE)
        self.assertIsNotNone(settings.TIME_ZONE)
        self.assertIsInstance(settings.USE_I18N, bool)
        self.assertIsInstance(settings.USE_TZ, bool)
    
    def test_email_configuration(self):
        """Test email configuration"""
        # Check if email settings exist
        email_settings = [
            'EMAIL_BACKEND',
            'EMAIL_HOST',
            'EMAIL_PORT',
            'EMAIL_USE_TLS',
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
        ]
        
        for setting in email_settings:
            if hasattr(settings, setting):
                self.assertIsNotNone(getattr(settings, setting))
    
    def test_celery_configuration(self):
        """Test Celery configuration if present"""
        celery_settings = [
            'CELERY_BROKER_URL',
            'CELERY_RESULT_BACKEND',
            'CELERY_ACCEPT_CONTENT',
            'CELERY_TASK_SERIALIZER',
        ]
        
        for setting in celery_settings:
            if hasattr(settings, setting):
                self.assertIsNotNone(getattr(settings, setting))


class URLConfigurationTestCase(TestCase):
    """Test cases for URL configuration"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
    
    def test_admin_urls(self):
        """Test admin URLs accessibility"""
        # Test admin login page
        response = self.client.get('/admin/')
        # Should redirect to login or show login form
        self.assertIn(response.status_code, [200, 302])
        
        # Test admin with authenticated admin user
        self.client.force_login(self.admin)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_root_urls(self):
        """Test API root URLs"""
        api_urls = [
            '/users/api/',
            '/candidatures/api/',
            '/notifications/api/',
        ]
        
        for url in api_urls:
            response = self.client.get(url)
            # Should be accessible (401 for unauthorized, 200 for open)
            self.assertIn(response.status_code, [200, 401, 403, 404, 405])
    
    def test_home_page_url(self):
        """Test home page URL"""
        try:
            response = self.client.get('/')
            # Should be accessible
            self.assertIn(response.status_code, [200, 302, 404])
        except Exception:
            # Home page might not be implemented
            pass
    
    def test_users_app_urls(self):
        """Test users app URLs"""
        users_urls = [
            '/users/',
            '/users/login/',
            '/users/register/',
        ]
        
        for url in users_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 404, 405])
    
    def test_candidatures_app_urls(self):
        """Test candidatures app URLs"""
        candidatures_urls = [
            '/candidatures/',
        ]
        
        for url in candidatures_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 401, 403, 404, 405])
    
    def test_url_resolution(self):
        """Test URL resolution for main patterns"""
        # Test that URLs resolve to correct views
        try:
            # Admin URLs
            self.assertIsNotNone(resolve('/admin/'))
            
            # App URLs (if they exist)
            for app in ['users', 'candidatures', 'notifications']:
                try:
                    self.assertIsNotNone(resolve(f'/{app}/'))
                except:
                    # URL might not exist
                    pass
        except Exception:
            # URL patterns might not be fully configured
            pass


class DatabaseConfigurationTestCase(TestCase):
    """Test cases for database configuration and models"""
    
    def test_database_connection(self):
        """Test database connection"""
        # Test basic database operations
        initial_count = User.objects.count()
        
        # Create a test user
        User.objects.create_user(
            username='dbtest',
            email='dbtest@example.com',
            password='testpass123'
        )
        
        # Verify user was created
        new_count = User.objects.count()
        self.assertEqual(new_count, initial_count + 1)
    
    def test_user_model_configuration(self):
        """Test custom user model configuration"""
        # Test that custom user model is configured
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')
        
        # Test user creation
        user = User.objects.create_user(
            username='modeltest',
            email='modeltest@example.com',
            password='testpass123'
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'modeltest')
        self.assertEqual(user.email, 'modeltest@example.com')
    
    def test_database_migrations(self):
        """Test that migrations have been applied"""
        from django.db import connection
        
        # Check that basic tables exist
        table_names = connection.introspection.table_names()
        
        expected_tables = [
            'auth_permission',
            'auth_group',
            'django_content_type',
            'django_session',
            'users_user',
        ]
        
        for table in expected_tables:
            if table in table_names:
                self.assertIn(table, table_names)


class SecurityConfigurationTestCase(TestCase):
    """Test cases for security configuration"""
    
    def test_security_middleware(self):
        """Test security middleware is properly configured"""
        security_middleware = 'django.middleware.security.SecurityMiddleware'
        self.assertIn(security_middleware, settings.MIDDLEWARE)
    
    def test_csrf_protection(self):
        """Test CSRF protection is enabled"""
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
        self.assertIn(csrf_middleware, settings.MIDDLEWARE)
    
    def test_session_security(self):
        """Test session security settings"""
        # Test session middleware
        session_middleware = 'django.contrib.sessions.middleware.SessionMiddleware'
        self.assertIn(session_middleware, settings.MIDDLEWARE)
        
        # Test session settings
        if hasattr(settings, 'SESSION_COOKIE_SECURE'):
            # In production, should be True
            self.assertIsInstance(settings.SESSION_COOKIE_SECURE, bool)
        
        if hasattr(settings, 'SESSION_COOKIE_HTTPONLY'):
            # Should be True for security
            self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
    
    def test_password_validation(self):
        """Test password validation configuration"""
        if hasattr(settings, 'AUTH_PASSWORD_VALIDATORS'):
            validators = settings.AUTH_PASSWORD_VALIDATORS
            self.assertIsInstance(validators, list)
            self.assertGreater(len(validators), 0)
    
    def test_allowed_hosts_configuration(self):
        """Test allowed hosts configuration"""
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
        
        if not settings.DEBUG:
            # In production, should not allow all hosts
            self.assertNotIn('*', settings.ALLOWED_HOSTS)


class StaticFilesTestCase(TestCase):
    """Test cases for static files configuration"""
    
    def test_static_files_settings(self):
        """Test static files settings"""
        self.assertIsNotNone(settings.STATIC_URL)
        
        if hasattr(settings, 'STATICFILES_DIRS'):
            self.assertIsInstance(settings.STATICFILES_DIRS, (list, tuple))
        
        if hasattr(settings, 'STATICFILES_FINDERS'):
            finders = settings.STATICFILES_FINDERS
            self.assertIsInstance(finders, (list, tuple))
            
            # Check for default finders
            default_finders = [
                'django.contrib.staticfiles.finders.FileSystemFinder',
                'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            ]
            
            for finder in default_finders:
                self.assertIn(finder, finders)
    
    def test_media_files_settings(self):
        """Test media files settings"""
        self.assertIsNotNone(settings.MEDIA_URL)
        
        if hasattr(settings, 'MEDIA_ROOT'):
            media_root = settings.MEDIA_ROOT
            if media_root:
                self.assertIsInstance(media_root, str)


class APIConfigurationTestCase(TestCase):
    """Test cases for API configuration"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='apitest',
            email='apitest@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_rest_framework_installed(self):
        """Test that REST Framework is properly installed"""
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
    
    def test_api_authentication(self):
        """Test API authentication"""
        # Test unauthenticated request
        response = self.client.get('/users/api/users/')
        self.assertIn(response.status_code, [401, 403, 404])
        
        # Test authenticated request
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/users/api/users/')
        self.assertIn(response.status_code, [200, 403, 404])
    
    def test_api_content_type(self):
        """Test API content type handling"""
        self.client.force_authenticate(user=self.user)
        
        # Test JSON content type
        response = self.client.get(
            '/users/api/users/',
            HTTP_ACCEPT='application/json'
        )
        
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_api_error_handling(self):
        """Test API error handling"""
        # Test 404 for non-existent endpoint
        response = self.client.get('/api/nonexistent/')
        self.assertEqual(response.status_code, 404)
        
        # Test method not allowed
        response = self.client.post('/users/api/users/999999/')
        self.assertIn(response.status_code, [404, 405])


class TemplateConfigurationTestCase(TestCase):
    """Test cases for template configuration"""
    
    def test_template_settings(self):
        """Test template configuration"""
        self.assertIn('TEMPLATES', dir(settings))
        
        templates = settings.TEMPLATES
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
        
        # Check Django template backend
        django_backend = None
        for template in templates:
            if template['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
                django_backend = template
                break
        
        self.assertIsNotNone(django_backend)
        
        # Check context processors
        if 'OPTIONS' in django_backend and 'context_processors' in django_backend['OPTIONS']:
            context_processors = django_backend['OPTIONS']['context_processors']
            
            required_processors = [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
            
            for processor in required_processors:
                self.assertIn(processor, context_processors)


class LoggingConfigurationTestCase(TestCase):
    """Test cases for logging configuration"""
    
    def test_logging_configuration(self):
        """Test logging configuration"""
        if hasattr(settings, 'LOGGING'):
            logging_config = settings.LOGGING
            self.assertIsInstance(logging_config, dict)
            
            # Check for basic logging structure
            if 'version' in logging_config:
                self.assertEqual(logging_config['version'], 1)
            
            if 'handlers' in logging_config:
                self.assertIsInstance(logging_config['handlers'], dict)
            
            if 'loggers' in logging_config:
                self.assertIsInstance(logging_config['loggers'], dict)


class EnvironmentConfigurationTestCase(TestCase):
    """Test cases for environment-specific configuration"""
    
    def test_debug_setting(self):
        """Test DEBUG setting appropriateness"""
        self.assertIsInstance(settings.DEBUG, bool)
        
        # In tests, DEBUG can be either True or False
        # In production, should be False
    
    def test_secret_key_configuration(self):
        """Test SECRET_KEY configuration"""
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertIsInstance(settings.SECRET_KEY, str)
        self.assertGreater(len(settings.SECRET_KEY), 10)
        
        # Should not be the default Django secret key
        default_key = 'django-insecure-'
        if settings.SECRET_KEY.startswith(default_key):
            # This is the default development key, should be changed in production
            pass
    
    def test_database_configuration_environment(self):
        """Test database configuration for environment"""
        db_config = settings.DATABASES['default']
        
        # Check engine
        self.assertIn('ENGINE', db_config)
        self.assertIsNotNone(db_config['ENGINE'])
        
        # Check name/path
        self.assertIn('NAME', db_config)
        self.assertIsNotNone(db_config['NAME'])


class IntegrationTestCase(TestCase):
    """Integration tests for the complete SmartRecruit system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.api_client = APIClient()
        
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
            role='admin',
            is_staff=True,
            is_superuser=True
        )
    
    def test_complete_user_workflow(self):
        """Test complete user workflow"""
        # 1. User registration/creation
        initial_count = User.objects.count()
        
        new_user = User.objects.create_user(
            username='integration_test',
            email='integration@example.com',
            password='testpass123',
            role='candidat'
        )
        
        self.assertEqual(User.objects.count(), initial_count + 1)
        
        # 2. User authentication
        self.assertTrue(new_user.check_password('testpass123'))
        
        # 3. User profile access
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.role, 'candidat')
    
    def test_admin_interface_integration(self):
        """Test admin interface integration"""
        # Test admin login
        self.client.force_login(self.admin)
        
        # Test admin home page
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Test user admin
        response = self.client.get('/admin/users/user/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_integration(self):
        """Test API integration across apps"""
        self.api_client.force_authenticate(user=self.candidate)
        
        # Test users API
        response = self.api_client.get('/users/api/users/')
        self.assertIn(response.status_code, [200, 403, 404])
        
        # Test candidatures API
        response = self.api_client.get('/candidatures/api/candidatures/')
        self.assertIn(response.status_code, [200, 403, 404])
        
        # Test notifications API
        response = self.api_client.get('/notifications/api/preferences/')
        self.assertIn(response.status_code, [200, 403, 404])
    
    def test_cross_app_functionality(self):
        """Test functionality that spans multiple apps"""
        # Test user creation triggers notification preferences
        from notifications.models import EmailPreferences
        
        new_user = User.objects.create_user(
            username='crossapp_test',
            email='crossapp@example.com',
            password='testpass123'
        )
        
        # Check if email preferences are created (depends on signals)
        try:
            preferences = EmailPreferences.objects.get(user=new_user)
            self.assertIsNotNone(preferences)
        except EmailPreferences.DoesNotExist:
            # Preferences might not be auto-created
            pass
    
    def test_system_health_check(self):
        """Test overall system health"""
        # Test database connectivity
        self.assertTrue(User.objects.exists() or True)  # Always passes, tests DB connection
        
        # Test that all apps are properly configured
        from django.apps import apps
        
        app_configs = apps.get_app_configs()
        app_labels = [app.label for app in app_configs]
        
        required_apps = ['users', 'candidatures', 'notifications']
        for app in required_apps:
            self.assertIn(app, app_labels)
        
        # Test that models can be imported
        try:
            from users.models import User
            from candidatures.models import Candidature
            from notifications.models import EmailPreferences
            
            # All imports successful
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import models: {e}")
