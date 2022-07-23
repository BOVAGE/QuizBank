from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
LOGIN_URL = reverse("authentication:login")
REGISTER_URL = reverse("authentication:register")
REFRESH_URL = reverse("authentication:token-refresh")
CHANGE_PWD_URL = reverse("authentication:change-password")

class LoginViewTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="bovage", 
        password="bovage123", email="b@gmail.com")
        self.verified_user = User.objects.create_user(username="dave", 
        password="dave1234", email="d@gmail.com", is_verified=True)

    def test_verification_required_login(self):
        """
            confirm that a user needs to verify his/her email account
            before login can be successful
        """
        body = {
            "username": "bovage",
            "password": "bovage123"
        }
        response = self.client.post(LOGIN_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")

    def test_invalid_credentials(self):
        """

        """
        body = {
            "username": "bovag",
            "password": "bovage12"
        }
        response = self.client.post(LOGIN_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")


    def test_success_login(self):
        """

        """
        body = {
            "username": "dave",
            "password": "dave1234"
        }
        response = self.client.post(LOGIN_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertIsInstance(response.data.get('data'), dict)
        self.assertIn("access", response.data.get('data'))
        self.assertIn("refresh", response.data.get('data'))

class RegisterViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bovage",
        email="bovage@gmail.com", password="12345678")

    def test_successful_register(self):
        """

        """
        body = {
            "username": "john",
            "email": "john@gmail.com",
            "password": "q1w2e3r4",
            "password2": "q1w2e3r4",
        }
        response = self.client.post(REGISTER_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertIsInstance(response.data.get('data'), dict)
        self.assertIn("username", response.data.get('data'))
        self.assertIn("email", response.data.get('data'))
        self.assertNotIn("password", response.data.get('data'))
        self.assertNotIn("password2", response.data.get('data'))

    def test_unique_validation(self):
        """

        """
        body = {
            "username": "bovage",
            "email": "bovage@gmail.com",
            "password": "q1w2e3r4",
            "password2": "q1w2e3r4",
        }
        response = self.client.post(REGISTER_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")
        self.assertIn("username", response.data.get("error"))
        self.assertIn("email", response.data.get("error"))

    def test_password_match(self):
        """

        """
        body = {
            "username": "john",
            "email": "john@gmail.com",
            "password": "q1w2e3t4",
            "password2": "q1w2e3r4",
        }
        response = self.client.post(REGISTER_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")
        self.assertIsInstance(response.data.get("error"), list)
        self.assertNotIn("username", response.data.get("error"))
        self.assertNotIn("email", response.data.get("error"))
        
    def test_required_fields(self):
        """

        """
        body = dict()
        response = self.client.post(REGISTER_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")
        self.assertIsInstance(response.data.get("error"), dict)
        self.assertIn("username", response.data.get("error"))
        self.assertIn("email", response.data.get("error"))
        self.assertIn("password", response.data.get("error"))
        self.assertIn("password2", response.data.get("error"))


class RefreshTokenViewTest(APITestCase):
    def setUp(self):
        self.verified_user = User.objects.create_user(username="dave", 
        password="dave1234", email="d@gmail.com", is_verified=True)
    
    def obtain_refresh_token(self) -> str:
        """
            get token by sending credential to login endpoint.
        """
        body = {
            "username": "dave",
            "password": "dave1234"
        }
        response = self.client.post(LOGIN_URL, data=body)
        return response.data.get("data")["refresh"]
    
    def test_successful_refresh(self):
        body = {
            "refresh": self.obtain_refresh_token(),
        }
        response = self.client.post(REFRESH_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertIsInstance(response.data.get('data'), dict)
        self.assertIn("access", response.data.get('data'))

    def test_invalid_refresh(self):
        body = {
            "refresh": "invalid token",
        }
        response = self.client.post(REFRESH_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")

    def test_refresh_required(self):
        body = dict()
        response = self.client.post(REFRESH_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")
        self.assertIn("refresh", response.data.get("error"))


class ChangePasswordViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="bovage", 
        password="bovage123", email="b@gmail.com")
        self.verified_user = User.objects.create_user(username="dave", 
        password="dave1234", email="d@gmail.com", is_verified=True)
    
    def test_successful_change(self):
        access_token = self.verified_user.get_tokens_for_user()["access"]
        body = {
            "old_password": "dave1234",
            "new_password": "newdave1234",
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(CHANGE_PWD_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.verified_user.refresh_from_db()
        self.assertFalse(self.verified_user.check_password(body["old_password"]))
        self.assertTrue(self.verified_user.check_password(body["new_password"]))

    def test_wrong_old(self):
        access_token = self.verified_user.get_tokens_for_user()["access"]
        body = {
            "old_password": "wrongold",
            "new_password": "newdave1234",
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(CHANGE_PWD_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")

    def test_unsuccessful_change(self):
        access_token = self.verified_user.get_tokens_for_user()["access"]
        body = dict()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(CHANGE_PWD_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")

    def test_auth_token_required(self):
        body = {
            "old_password": "dave1234",
            "new_password": "newdave1234",
        }
        response = self.client.post(CHANGE_PWD_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")
