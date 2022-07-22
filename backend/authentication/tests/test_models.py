import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()
SIGNING_KEY = settings.SIMPLE_JWT['SIGNING_KEY']
ALGORITHM = settings.SIMPLE_JWT['ALGORITHM']
class UserModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="bovage", 
        password="12345678", email="bovage@gmail.com")
        self.superuser = User.objects.create_superuser(username="suser", 
        password="s1234567", email="suser@gmail.com")
        print("setting up")
        print(self.user.id, "ou in setUp")
        print(self.superuser.id, "su in setUp")

    def test_ordinary_user(self):
        ordinary_user = User.objects.get(username="bovage")
        print(ordinary_user.id, "ou")
        username = self.user.username
        email = self.user.email
        ordinary_user.check_password("12345678")
        self.assertEqual(ordinary_user.username, username)
        self.assertEqual(ordinary_user.email, email)
        self.assertEqual(ordinary_user.check_password("12345678"), True)
        self.assertEqual(ordinary_user.check_password("12348"), False)
        self.assertFalse(ordinary_user.is_staff)
        self.assertFalse(ordinary_user.is_superuser)
        self.assertFalse(ordinary_user.is_verified)
        self.assertTrue(ordinary_user.is_active)
    
    def test_super_user(self):
        super_user = User.objects.get(username="suser")
        print(super_user.id, "su")
        username = self.superuser.username
        email = self.superuser.email
        super_user.check_password("s12345678")
        self.assertEqual(super_user.username, username)
        self.assertEqual(super_user.email, email)
        self.assertEqual(super_user.check_password("s1234567"), True)
        self.assertEqual(super_user.check_password("12348"), False)
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_active)

    def test_access_and_refresh_tokens(self):
        dict_token = self.user.get_tokens_for_user()
        self.assertIsInstance(dict_token, dict)
        self.assertIn("refresh", dict_token)
        self.assertIn("access", dict_token)
        access_token = dict_token['access']
        id_from_token = jwt.decode(access_token, SIGNING_KEY, [ALGORITHM])['user_id']
        self.assertEqual(self.user.id, id_from_token)
    
    def test_user_question(self):
        total_questions = self.user.get_number_of_questions()
        total_verified_questions = self.user.get_number_of_verified_questions()
        total_unverified_questions = self.user.get_number_of_unverified_questions()
        self.assertIsInstance(total_questions, int)
        self.assertIsInstance(total_verified_questions, int)
        self.assertIsInstance(total_unverified_questions, int)
        self.assertEqual(total_questions, 0)
        self.assertEqual(total_verified_questions, 0)
        self.assertEqual(total_unverified_questions, 0)

    def test_user_stat(self):
        self.assertIsInstance(User.total_user(), int)
        self.assertIsInstance(User.total_staff(), int)
        self.assertEqual(User.total_user(), User.objects.count())
        self.assertEqual(User.total_user(), 2)
        self.assertEqual(User.total_staff(), 1)

    def test_default_user_avatar(self):
        """
            to test the default image.
        """
        self.assertIsNotNone(self.user.avatar)

    def test_user_creation_validation(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="bovage", 
            password="12345678", email="bovage@gmail.com")

