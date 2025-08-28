from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


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
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_recruiter_can_list_candidates_and_recruiters(self):
        """Test that recruiter can see candidates and recruiters but not admins"""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see recruiter and candidate, but not admin
        self.assertEqual(len(response.data['results']), 2)
    
    def test_candidate_can_only_see_own_profile(self):
        """Test that candidate can only see their own profile"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.candidate_user.id)
    
    def test_admin_can_change_user_role(self):
        """Test that admin can change user roles"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/users/{self.candidate_user.id}/change_role/',
            {'role': 'recruteur'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
