from datetime import datetime

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
STATISTICS_URL = reverse("statistics")


class PublicQuestionListTest(APITestCase):
    def setUp(self):
        self.verified_user = User.objects.create_user(
            username="dave", password="dave1234", email="d@gmail.com", is_verified=True
        )
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?",
            difficulty="easy",
            type="True / False",
            created_by=self.verified_user,
            correct_answer="True",
            explanation="cause I'm old",
            category=self.category,
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
        self.assertEqual(response.data.get("status"), "success")
        self.assertEqual(len(response.data.get("data")), 0)

    def test_question_list_verified(self):
        """
        confirms that the public endpoint contains only verified
        questions.
        """
        question = Question.objects.create(
            question="Are you old?",
            difficulty="easy",
            type="True / False",
            created_by=self.verified_user,
            correct_answer="True",
            explanation="cause I'm old",
            category=self.category,
        )
        question.verify(self.verified_user)
        self.question_1.verify(self.verified_user)
        response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertEqual(len(response.data.get("data")), 2)

    def test_question_limit(self):
        """
        confirms that the number of verified questions returned
        is not more than the limit set.
        """
        for i in range(LIMIT + 2):
            question = Question.objects.create(
                question=f"{i} Are you old?",
                difficulty="easy",
                type="True / False",
                created_by=self.verified_user,
                correct_answer="True",
                explanation="cause I'm old",
                category=self.category,
            )
            question.verify(self.verified_user)
            response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertLessEqual(len(response.data.get("data")), LIMIT)

    def test_question_limit(self):
        """
        confirms that the number of verified questions returned
        is not more than the limit set.
        """
        for i in range(LIMIT + 2):
            question = Question.objects.create(
                question=f"{i} Are you old?",
                difficulty="easy",
                type="True / False",
                created_by=self.verified_user,
                correct_answer="True",
                explanation="cause I'm old",
                category=self.category,
            )
            question.verify(self.verified_user)
        response = self.client.get(QUESTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertLessEqual(len(response.data.get("data")), LIMIT)

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
        self.assertEqual(response.data.get("status"), "error")

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
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.post(QUESTION_URL, format="json", data=body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")


class QuestionListFullViewTest(APITestCase):
    def setUp(self):
        self.verified_user = User.objects.create_user(
            username="dave", password="dave1234", email="d@gmail.com", is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="dave1234",
            email="admin@gmail.com",
            is_verified=True,
        )
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?",
            difficulty="easy",
            type="True / False",
            created_by=self.verified_user,
            correct_answer="True",
            explanation="cause I'm old",
            category=self.category,
        )
        self.question_1.verify(self.admin_user)

    def test_admin_restriction(self):
        """
        confirms that only an admin user can access the full question
        endpoint
        """
        access_token = self.verified_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(QUESTION_LIST_FULL_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get("status"), "error")

    def test_successful_question_list_for_admin(self):
        access_token = self.admin_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(QUESTION_LIST_FULL_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")

    def test_response_is_paginated(self):
        """
        confirms that the response is paginated.
        """
        access_token = self.admin_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(QUESTION_LIST_FULL_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data.get("data"), dict)
        self.assertIn("count", response.data.get("data"))
        self.assertIn("previous", response.data.get("data"))
        self.assertIn("next", response.data.get("data"))
        self.assertIn("results", response.data.get("data"))
        self.assertIsInstance(response.data.get("data")["results"], list)

    def test_response_data_is_detailed(self):
        """
        confirms that the response is more detailed. i.e
        contains more info like verified_by, date_verified
        """
        access_token = self.admin_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(QUESTION_LIST_FULL_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("data")["results"]
        self.assertIn("date_verified", results[0])
        self.assertIn("verified_by", results[0])
        self.assertIn("created_by", results[0])


class QuestionVerificationTest(APITestCase):
    def setUp(self):
        self.verified_user = User.objects.create_user(
            username="dave", password="dave1234", email="d@gmail.com", is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="dave1234",
            email="admin@gmail.com",
            is_verified=True,
        )
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?",
            difficulty="easy",
            type="True / False",
            created_by=self.admin_user,
            correct_answer="True",
            explanation="cause I'm old",
            category=self.category,
        )

    def get_question_verification_url(self) -> str:
        """
        returns the url for question verification based on
        the question id in setUp, so the test can be independent of
        other tests
        """
        return reverse("quiz:question-verification", args=(self.question_1.id,))

    def test_admin_restriction(self):
        """
        confirms that only an admin user can handle full question
        verification.
        """
        access_token = self.verified_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.post(self.get_question_verification_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("error", response.data)
        self.assertNotIn("data", response.data)
        self.assertEqual(response.data.get("status"), "error")

    def test_successful_verification(self):
        """
        confirms that a question can be verified successfully
        by an admin user
        """
        access_token = self.admin_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.post(self.get_question_verification_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.question_1.refresh_from_db()
        self.assertTrue(self.question_1.is_verified)
        self.assertIsInstance(self.question_1.verified_by, User)
        self.assertIsInstance(self.question_1.date_verified, datetime)

    def test_successful_unverification(self):
        """
        confirms that a question can be unverified successfully
        by an admin user
        """
        access_token = self.admin_user.get_tokens_for_user()["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.delete(self.get_question_verification_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.question_1.refresh_from_db()
        self.assertFalse(self.question_1.is_verified)
        self.assertIsNone(self.question_1.verified_by)
        self.assertIsNone(self.question_1.date_verified)


class StatisticsViewTest(APITestCase):
    def setUp(self):
        self.verified_user = User.objects.create_user(
            username="dave", password="dave1234", email="d@gmail.com", is_verified=True
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="dave1234",
            email="admin@gmail.com",
            is_verified=True,
        )
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?",
            difficulty="easy",
            type="True / False",
            created_by=self.verified_user,
            correct_answer="True",
            explanation="cause I'm old",
            category=self.category,
        )
        self.question_1.verify(self.admin_user)

    def test_success_request(self):
        response = self.client.get(STATISTICS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertIsInstance(response.data.get("data"), dict)
        self.assertIn("question", response.data.get("data"))
        self.assertIn("difficulty", response.data.get("data"))
        self.assertIn("category", response.data.get("data"))
        self.assertIn("users", response.data.get("data"))
        self.assertIn("activity", response.data.get("data"))

    def test_filtering_category(self):
        response = self.client.get(STATISTICS_URL + "?on=category")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertIn("category", response.data.get("data"))
        self.assertEqual(len(response.data.get("data")), 1)

    def test_filtering_difficulty(self):
        """
        confirms filtering returns the result contains
        difficulty only.
        """
        response = self.client.get(STATISTICS_URL + "?on=difficulty")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertIn("difficulty", response.data.get("data"))
        self.assertEqual(len(response.data.get("data")), 1)

    def test_filtering_question(self):
        response = self.client.get(STATISTICS_URL + "?on=question")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertIn("question", response.data.get("data"))
        self.assertEqual(len(response.data.get("data")), 1)

    def test_filtering_users(self):
        response = self.client.get(STATISTICS_URL + "?on=users")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertIn("users", response.data.get("data"))
        self.assertEqual(len(response.data.get("data")), 1)

    def test_filtering_activity(self):
        response = self.client.get(STATISTICS_URL + "?on=activity")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("data", response.data)
        self.assertNotIn("error", response.data)
        self.assertEqual(response.data.get("status"), "success")
        self.assertIn("activity", response.data.get("data"))
        self.assertEqual(len(response.data.get("data")), 1)
