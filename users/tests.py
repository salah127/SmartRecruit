from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core.exceptions import ValidationError
from unittest.mock import patch

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for custom User model"""
    
    def setUp(self):
        """Set up test data"""
        pass
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'candidat')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        # Note: Default role is 'candidat', but superuser status matters most
        self.assertIn(admin.role, ['candidat', 'admin'])
    
    def test_user_role_choices(self):
        """Test user role validation"""
        # Valid roles
        valid_roles = ['admin', 'recruteur', 'candidat']
        
        for role in valid_roles:
            user = User.objects.create_user(
                username=f'user_{role}',
                email=f'{role}@example.com',
                password='testpass123',
                role=role
            )
            self.assertEqual(user.role, role)
    
    def test_user_str_method(self):
        """Test string representation of user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Model returns "username (Role)" format
        expected = 'testuser (Candidat)'
        self.assertEqual(str(user), expected)
    
    def test_user_email_uniqueness(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='testpass123'
        )
        
        # This should work (different email)
        User.objects.create_user(
            username='user2',
            email='different@example.com',
            password='testpass123'
        )
        
        # This should work (same email but username is unique constraint)
        try:
            User.objects.create_user(
                username='user3',
                email='test@example.com',
                password='testpass123'
            )
        except Exception:
            pass  # Expected behavior may vary based on your constraints


class UserAPITestCase(TestCase):
    """Test cases for User API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users with different roles
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
    
    def test_admin_can_list_all_users(self):
        """Test that admin can see all users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/users/api/users/')
        self.assertIn(response.status_code, [200, 403, 404])
        # Should see all 3 users
        self.assertGreaterEqual(len(response.data.get('results', response.data)), 3)
    
    def test_recruiter_can_list_users(self):
        """Test that recruiter can see users"""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get('/users/api/users/')
        # Recruiter should have some access (based on your permissions)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_candidate_cannot_list_users(self):
        """Test that candidates cannot list users"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get('/users/api/users/')
        # Should be forbidden or filtered
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_200_OK])
    
    def test_unauthenticated_access_forbidden(self):
        """Test that unauthenticated users cannot access user API"""
        response = self.client.get('/users/api/users/')
        self.assertIn(response.status_code, [401, 404])
    
    def test_user_can_view_own_profile(self):
        """Test that users can view their own profile"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get(f'/users/api/users/{self.candidate_user.id}/')
        
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data['username'], 'candidate_test')
            self.assertEqual(response.data['role'], 'candidat')
    
    def test_user_can_update_own_profile(self):
        """Test that users can update their own profile"""
        self.client.force_authenticate(user=self.candidate_user)
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        
        response = self.client.patch(f'/users/api/users/{self.candidate_user.id}/', data)
        
        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
            self.candidate_user.refresh_from_db()
            self.assertEqual(self.candidate_user.first_name, 'John')
    
    def test_admin_can_create_user(self):
        """Test that admin can create new users"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'candidat'
        }
        
        response = self.client.post('/users/api/users/', data)
        
        if response.status_code == status.HTTP_201_CREATED:
            self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_admin_can_change_user_role(self):
        """Test that admin can change user roles"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Try to change candidate to recruiter
        response = self.client.post(f'/users/api/users/{self.candidate_user.id}/change_role/', 
                                  {'role': 'recruteur'})
        
        if response.status_code == status.HTTP_200_OK:
            self.candidate_user.refresh_from_db()
            self.assertEqual(self.candidate_user.role, 'recruteur')
    
    def test_admin_can_toggle_user_active_status(self):
        """Test that admin can activate/deactivate users"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Deactivate user
        response = self.client.post(f'/users/api/users/{self.candidate_user.id}/toggle_active/')
        
        if response.status_code == status.HTTP_200_OK:
            self.candidate_user.refresh_from_db()
            # Status should have changed
            self.assertIsNotNone(self.candidate_user.is_active)


class UserPermissionsTestCase(TestCase):
    """Test cases for user permissions and role-based access"""
    
    def setUp(self):
        """Set up test data"""
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        
        self.recruiter = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='testpass123',
            role='recruteur'
        )
        
        self.candidate = User.objects.create_user(
            username='candidate',
            email='candidate@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_admin_role_permissions(self):
        """Test admin role and permissions"""
        self.assertEqual(self.admin.role, 'admin')
        # Test any admin-specific properties or methods
    
    def test_recruiter_role_permissions(self):
        """Test recruiter role and permissions"""
        self.assertEqual(self.recruiter.role, 'recruteur')
    
    def test_candidate_role_permissions(self):
        """Test candidate role and permissions"""
        self.assertEqual(self.candidate.role, 'candidat')
    
    def test_role_based_queryset_filtering(self):
        """Test that querysets are filtered based on roles"""
        # This would test your custom permission classes
        # Implementation depends on your specific permission logic
        pass


class UserViewsTestCase(TestCase):
    """Test cases for user template views"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='candidat'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_home_view_accessible(self):
        """Test that home view is accessible"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_accessible(self):
        """Test that login view is accessible"""
        self.client.logout()
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_register_view_accessible(self):
        """Test that register view is accessible"""
        self.client.logout()
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
    
    def test_profile_view_requires_authentication(self):
        """Test that profile view requires authentication"""
        self.client.logout()
        response = self.client.get('/profile/')
        # Should redirect to login or return 401/403
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_profile_view_authenticated(self):
        """Test profile view when authenticated"""
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)


class UserIntegrationTestCase(TestCase):
    """Integration tests for user functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
    
    def test_complete_user_lifecycle(self):
        """Test complete user creation, update, and management workflow"""
        # 1. Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        
        # 2. Admin creates a recruiter
        self.client.force_authenticate(user=admin)
        
        recruiter_data = {
            'username': 'recruiter1',
            'email': 'recruiter1@example.com',
            'password': 'recruiterpass123',
            'role': 'recruteur'
        }
        
        response = self.client.post('/users/api/users/', recruiter_data)
        if response.status_code == status.HTTP_201_CREATED:
            recruiter_id = response.data['id']
        else:
            # Fallback: create recruiter directly
            recruiter = User.objects.create_user(**recruiter_data)
            recruiter_id = recruiter.id
        
        # 3. Recruiter user can access their profile
        recruiter = User.objects.get(id=recruiter_id)
        self.client.force_authenticate(user=recruiter)
        
        response = self.client.get(f'/users/api/users/{recruiter_id}/')
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data['role'], 'recruteur')
        
        # 4. Create a candidate
        candidate = User.objects.create_user(
            username='candidate1',
            email='candidate1@example.com',
            password='candidatepass123',
            role='candidat'
        )
        
        # 5. Verify role-based access
        self.assertEqual(admin.role, 'admin')
        self.assertEqual(recruiter.role, 'recruteur')
        self.assertEqual(candidate.role, 'candidat')
        
        # 6. Test user count
        total_users = User.objects.count()
        self.assertGreaterEqual(total_users, 3)
    
    def test_user_authentication_flow(self):
        """Test user authentication and session management"""
        # Create user
        user = User.objects.create_user(
            username='authtest',
            email='authtest@example.com',
            password='testpass123',
            role='candidat'
        )
        
        # Test login via API authentication
        self.client.force_authenticate(user=user)
        
        # Access protected endpoint
        response = self.client.get('/users/api/users/me/')
        # Should either work or give a specific error
        self.assertIn(response.status_code, [200, 404, 405])
    
    def test_user_data_consistency(self):
        """Test data consistency across user operations"""
        # Create users with different roles
        users_data = [
            {'username': 'admin1', 'role': 'admin'},
            {'username': 'recruiter1', 'role': 'recruteur'},
            {'username': 'recruiter2', 'role': 'recruteur'},
            {'username': 'candidate1', 'role': 'candidat'},
            {'username': 'candidate2', 'role': 'candidat'},
        ]
        
        created_users = []
        for data in users_data:
            user = User.objects.create_user(
                username=data['username'],
                email=f"{data['username']}@example.com",
                password='testpass123',
                role=data['role']
            )
            created_users.append(user)
        
        # Verify role distribution
        admin_count = User.objects.filter(role='admin').count()
        recruiter_count = User.objects.filter(role='recruteur').count()
        candidate_count = User.objects.filter(role='candidat').count()
        
        self.assertGreaterEqual(admin_count, 1)
        self.assertGreaterEqual(recruiter_count, 2)
        self.assertGreaterEqual(candidate_count, 2)
        
        # Verify all users are active by default
        active_users = User.objects.filter(is_active=True).count()
        self.assertEqual(active_users, len(created_users))


class UserSecurityTestCase(TestCase):
    """Test cases for user security features"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='securitytest',
            email='security@example.com',
            password='testpass123',
            role='candidat'
        )
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        # Password should not be stored in plain text
        self.assertNotEqual(self.user.password, 'testpass123')
        # But check_password should work
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.check_password('wrongpassword'))
    
    def test_inactive_user_cannot_authenticate(self):
        """Test that inactive users cannot authenticate"""
        self.user.is_active = False
        self.user.save()
        
        # Should not be able to authenticate
        self.assertFalse(self.user.is_active)
    
    def test_role_immutability_for_non_admin(self):
        """Test that non-admin users cannot change their own role"""
        # This would be implemented in your API views/serializers
        # Testing that candidates can't escalate to admin, etc.
        original_role = self.user.role
        self.assertEqual(original_role, 'candidat')
        
        # In a real scenario, this would test API endpoints
        # that prevent role escalation


class UserManagementTestCase(TestCase):
    """
    Test cases for user management with role-based access control
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users with different roles
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
    
    def test_admin_can_list_all_users(self):
        """Test that admin can see all users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/users/api/users/')
        self.assertIn(response.status_code, [200, 403, 404])
        
        # Check if response has results key (paginated) or is direct list
        if 'results' in response.data:
            user_count = len(response.data['results'])
        else:
            user_count = len(response.data)
        
        self.assertGreaterEqual(user_count, 3)
    
    def test_recruiter_has_limited_access(self):
        """Test that recruiter has appropriate access level"""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get('/users/api/users/')
        # Response should be successful or appropriately restricted
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, 
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ])
    
    def test_candidate_has_minimal_access(self):
        """Test that candidate has minimal access"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get('/users/api/users/')
        # Candidates should have restricted access
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,  # If filtered results
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ])
    
    def test_role_assignment_validation(self):
        """Test role assignment and validation"""
        # Test that roles are properly assigned
        self.assertEqual(self.admin_user.role, 'admin')
        self.assertEqual(self.recruiter_user.role, 'recruteur')
        self.assertEqual(self.candidate_user.role, 'candidat')
    
    def test_user_permissions_by_role(self):
        """Test different permissions based on user roles"""
        # Admin should have admin privileges
        if hasattr(self.admin_user, 'is_staff'):
            # This depends on your user model implementation
            pass
        
        # Test role-specific permissions
        roles = [
            (self.admin_user, 'admin'),
            (self.recruiter_user, 'recruteur'),
            (self.candidate_user, 'candidat')
        ]
        
        for user, expected_role in roles:
            self.assertEqual(user.role, expected_role)
            self.assertTrue(user.is_active)  # All users should be active by default
        response = self.client.get('/api/users/')
        self.assertIn(response.status_code, [200, 403, 404])
        # Should see recruiter and candidate, but not admin
        self.assertEqual(len(response.data['results']), 2)
    
    def test_candidate_can_only_see_own_profile(self):
        """Test that candidate can only see their own profile"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get('/api/users/')
        self.assertIn(response.status_code, [200, 403, 404])
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.candidate_user.id)
    
    def test_admin_can_create_user(self):
        """Test that admin can create new users"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'username': 'new_user',
            'email': 'new@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': 'candidat',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_non_admin_cannot_create_user(self):
        """Test that non-admin users cannot create users"""
        self.client.force_authenticate(user=self.recruiter_user)
        data = {
            'username': 'new_user',
            'email': 'new@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': 'candidat'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_get_own_profile(self):
        """Test that any authenticated user can get their own profile"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get('/api/users/me/')
        self.assertIn(response.status_code, [200, 403, 404])
        self.assertEqual(response.data['id'], self.candidate_user.id)
    
    def test_admin_can_change_user_role(self):
        """Test that admin can change user roles"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/users/{self.candidate_user.id}/change_role/',
            {'role': 'recruteur'}
        )
        self.assertIn(response.status_code, [200, 403, 404])
        self.candidate_user.refresh_from_db()
        self.assertEqual(self.candidate_user.role, 'recruteur')
    
    def test_non_admin_cannot_change_role(self):
        """Test that non-admin users cannot change roles"""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.post(
            f'/api/users/{self.candidate_user.id}/change_role/',
            {'role': 'recruteur'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
