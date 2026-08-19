from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from .models import UserProfile
# Create your tests here.

class RegisterTestCase(APITestCase):
    def test_register_user(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "phone_number": "12345678901"
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_without_phone_number(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "phone_number": ""
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        """     def test_register_user_without_email(self):
        data = {
            "username": "testuser",
            "email": "",
            "password": "testpassword",
            "phone_number": "12345678901"
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        """

    def test_register_user_without_password(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "",
            "phone_number": "12345678901"
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_without_username(self):
        data = {
            "username": "",
            "email": "testuser@example.com",
            "password": "testpassword",
            "phone_number": "12345678901"
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
