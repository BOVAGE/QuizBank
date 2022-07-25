from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category, InCorrectAnswer, Question

User = get_user_model()
LIMIT = 50
QUESTION_URL = reverse("quiz:question-list")
QUESTION_DETAIL_URL = reverse("quiz:question-detail", args="1")
QUESTION_LIST_FULL_URL = reverse("quiz:question-list-full")
UNVERIFIED_QUESTION_LIST_URL = reverse("quiz:unverified-question-list-full")
QUESTION_VERIFICATION_URL = reverse("quiz:question-verification", args="1")

class PublicQuestionListTest(APITestCase):
    def setUp(self):
        self.verified_user = User.objects.create_user(username="dave", 
        password="dave1234", email="d@gmail.com", is_verified=True)
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?", difficulty="eazy", type="True / False",
            created_by=self.verified_user, correct_answer="True", explanation="cause I'm old",
            category=self.category
        )
    
    def test_question_list_isempty(self):
        """
            confirms that the public endpoint does not contains
            only unverified questions
        """
        response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertEqual(len(response.data.get('data')), 0)
        
    
    def test_question_list_verified(self):
        """
            confirms that the public endpoint contains only verified
            questions.
        """
        question = Question.objects.create(
            question="Are you old?", difficulty="eazy", type="True / False",
            created_by=self.verified_user, correct_answer="True", explanation="cause I'm old",
            category=self.category
        )
        question.verify(self.verified_user)
        self.question_1.verify(self.verified_user)
        response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertEqual(len(response.data.get('data')), 2)

    def test_question_limit(self):
        """
            confirms that the number of verified questions returned
            is not more than the limit set.
        """
        for i in range(LIMIT+2):
            question = Question.objects.create(
            question=f"{i} Are you old?", difficulty="eazy", type="True / False",
            created_by=self.verified_user, correct_answer="True", explanation="cause I'm old",
            category=self.category
            )
            question.verify(self.verified_user)
            response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertLessEqual(len(response.data.get('data')), LIMIT)

    def test_question_limit(self):
        """
            confirms that the number of verified questions returned
            is not more than the limit set.
        """
        for i in range(LIMIT+2):
            question = Question.objects.create(
            question=f"{i} Are you old?", difficulty="eazy", type="True / False",
            created_by=self.verified_user, correct_answer="True", explanation="cause I'm old",
            category=self.category
            )
            question.verify(self.verified_user)
        response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")
        self.assertLessEqual(len(response.data.get('data')), LIMIT)
    
    def test_authentication_required_to_create(self):
        body = {
            "question": "Can I post a question without being authenticated?",
            "difficulty": "medium",
            "type": "True / False",
            "correct_answer": "False",
            "incorrect_answer_fields": {
                "incorrect_answer_1": "True",
            },
            "category": self.category.id,
        }
        response = self.client.post(QUESTION_URL, format="json", data=body)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get('status'), "error")

    def test_successful_successful_question_create(self):
        body = {
            "question": "Can I post a question without being authenticated?",
            "difficulty": "medium",
            "type": "True / False",
            "correct_answer": "False",
            "incorrect_answer_fields": {
                "incorrect_answer_1": "True",
            },
            "category": self.category.id,
        }
        access_token = self.verified_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(QUESTION_URL, format="json", data=body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get('status'), "success")