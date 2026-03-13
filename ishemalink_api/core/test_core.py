from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User

class TestUserRegistration(APITestCase):
    def test_user_registration(self):
        url = reverse('user-register')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'phone': '+250788123456',
            'user_type': 'AGENT',
            'assigned_sector': 'Kicukiro/Niboye'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

class TestNIDVerification(APITestCase):
    def test_valid_nid_format(self):
        # Add logic for valid NID test
        pass

    def test_invalid_nid_format(self):
        # Add logic for invalid NID test
        pass

class TestNIDVerification(APITestCase):
    def test_valid_nid_format(self):
        url = reverse('verify-nid')
        data = {'nid': '1234567890123456'}  # Example valid NID
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])

    def test_invalid_nid_format(self):
        url = reverse('verify-nid')
        data = {'nid': '12345'}  # Example invalid NID
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['valid'])
