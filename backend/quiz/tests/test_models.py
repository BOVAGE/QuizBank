from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import Category, InCorrectAnswer, Question

User = get_user_model()

class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test")
    
    def test_category_name(self):
        self.assertEqual("Test", self.category.name)

    def test_category_slug(self):
        self.assertEqual("test", self.category.slug)

    def test_category_stat(self):
        """
            confirms the category statistics is right.
        """
        self.assertIsInstance(Category.questions_count_category(), dict)
    
    def test_string_representation(self):
        self.assertEqual(str(self.category), self.category.name)


class QuestionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bovage", 
        password="12345678", email="bovage@gmail.com", is_verified=True)
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?", difficulty="easy", type="True / False",
            created_by=self.user, correct_answer="True", explanation="cause I'm old",
            category=self.category
        )

    def test_question_fields(self):
        self.assertEqual("Are you old?", self.question_1.question)
        self.assertEqual("easy", self.question_1.difficulty)
        self.assertEqual("True / False", self.question_1.type)
        self.assertEqual(self.user, self.question_1.created_by)
        self.assertEqual("True", self.question_1.correct_answer)
        self.assertEqual("cause I'm old", self.question_1.explanation)
        self.assertEqual("Are you old?", self.question_1.question)
        self.assertEqual(self.category, self.question_1.category)
        self.assertFalse(self.question_1.is_verified)
        self.assertIsNone(self.question_1.verified_by)

    def test_question_verification(self):
        self.question_1.verify(self.user)
        self.assertTrue(self.question_1.is_verified)
        self.assertIsNotNone(self.question_1.verified_by)
        self.assertIsInstance(self.question_1.date_verified, datetime)

    def test_verification_validation(self):
        with self.assertRaises(ValidationError):
            self.question_1.is_verified = True
            self.question_1.save()
        with self.assertRaises(ValidationError):
            self.question_1.verified_by = self.user
            self.question_1.save()
        self.question_1.date_verified = timezone.now()
        self.question_1.save()
       

    def test_question_unverification(self):
        self.question_1.unverify()
        self.assertFalse(self.question_1.is_verified)
        self.assertIsNone(self.question_1.verified_by)
        self.assertIsNone(self.question_1.date_verified)
        self.assertNotIsInstance(self.question_1.date_verified, datetime)
    
    def test_string_representation(self):
        self.assertEqual(str(self.question_1), self.question_1.question)

    def test_question_stat(self):
        """
            confirms the questions statistics is right.
        """
        total_questions = Question.objects.count()
        self.assertIsInstance(Question.no_of_all_questions(), int)
        self.assertIsInstance(Question.no_of_verified_questions(), int)
        self.assertIsInstance(Question.no_of_unverified_questions(), int)
        self.assertIsInstance(Question.no_of_easy_questions(), int)
        self.assertIsInstance(Question.no_of_medium_questions(), int)
        self.assertIsInstance(Question.no_of_hard_questions(), int)
        self.assertEqual(total_questions, Question.no_of_all_questions())


class IncorrectAnswerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bovage", 
        password="12345678", email="bovage@gmail.com", is_verified=True)
        self.category = Category.objects.create(name="Test")
        self.question_1 = Question.objects.create(
            question="Are you old?", difficulty="easy", type="True / False",
            created_by=self.user, correct_answer="True", explanation="cause I'm old",
            category=self.category
        )
        self.question_2 = Question.objects.create(
            question="Are you old?", difficulty="easy", type="multiple-choice",
            created_by=self.user, correct_answer="True", explanation="cause I'm old",
            category=self.category
        )
        self.incorrect_answer = InCorrectAnswer.objects.create(question=self.question_1, option="False")

    def test_trueorfalse_validation(self):
        with self.assertRaises(ValidationError):
            InCorrectAnswer.objects.create(question=self.question_1, option="fail")
        self.assertEqual(self.question_1.incorrect_answers.count(), 1)
    
    def test_multiple_choice_no_error(self):
        InCorrectAnswer.objects.create(question=self.question_2, option="Maybe")
        InCorrectAnswer.objects.create(question=self.question_2, option="Yes")
        InCorrectAnswer.objects.create(question=self.question_2, option="I don't Know")
    
    def test_string_representation(self):
        self.assertEqual(str(self.incorrect_answer), self.incorrect_answer.option)
