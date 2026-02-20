from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Test user registration endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@ishemalink.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'phone': '+250788123456',
            'user_type': 'CUSTOMER',
            'first_name': 'Test',
            'last_name': 'User',
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['phone'], '+250788123456')
    
    def test_user_registration_invalid_phone(self):
        """Test registration with invalid phone number"""
        data = {
            'username': 'testuser',
            'email': 'test@ishemalink.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'phone': '+256788123456',  # Uganda number
            'user_type': 'CUSTOMER',
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
    
    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'testuser',
            'email': 'test@ishemalink.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!',
            'phone': '+250788123456',
            'user_type': 'CUSTOMER',
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_phone(self):
        """Test registration with duplicate phone"""
        # Create first user
        User.objects.create_user(
            username='user1',
            email='user1@ishemalink.com',
            password='TestPass123!',
            phone='+250788123456'
        )
        
        # Try to register with same phone
        data = {
            'username': 'testuser2',
            'email': 'test2@ishemalink.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'phone': '+250788123456',
            'user_type': 'CUSTOMER',
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class NIDBatchVerificationTests(TestCase):
    """Test NID verification endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.verify_nid_url = '/api/auth/verify-nid/'
    
    def test_valid_nid_verification(self):
        """Test verification of valid NID"""
        data = {'nid': '1234567890123456'}
        response = self.client.post(self.verify_nid_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
    
    def test_invalid_nid_verification(self):
        """Test verification of invalid NID"""
        data = {'nid': '0234567890123456'}  # Starts with 0
        response = self.client.post(self.verify_nid_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['valid'])
        self.assertIn('error', response.data)
    
    def test_short_nid_verification(self):
        """Test verification of too short NID"""
        data = {'nid': '123456789'}
        response = self.client.post(self.verify_nid_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class HealthCheckTests(TestCase):
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test system health check"""
        response = self.client.get('/api/status/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('database', response.data)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = self.client.get('/api/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('api_version', response.data)
        self.assertIn('endpoints', response.data)
        self.assertEqual(response.data['project'], 'IshemaLink')
