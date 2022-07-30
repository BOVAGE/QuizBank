import datetime
import random
from typing import Dict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()
DIFFICULTY_CHOICES = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

TYPE_CHOICES = [
    ("multiple-choice", "Multiple Choice"),
    ("True / False", "True / False"),
]


def get_sentinel_category():
    return Category.objects.get_or_create(name="deleted")


class VerifiedManager(models.Manager):
    def get_queryset(self):
        return super(VerifiedManager, self).get_queryset().filter(is_verified=True)

    def random_all(self):
        order_field_asc = ["date_created", "category", "difficulty", "type"]
        order_field_desc = ["-date_created", "-category", "-difficulty", "-type"]
        random_order_asc = random.choice(order_field_asc)
        random_order_desc = random.choice(order_field_asc)
        queryset = self.get_queryset().order_by(random_order_asc, random_order_desc)
        return queryset


class UnVerifiedManager(models.Manager):
    def get_queryset(self):
        return super(UnVerifiedManager, self).get_queryset().filter(is_verified=False)


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def questions_count_category() -> Dict[str, int]:
        """
        returns a dict that contains all categories with the
        no of questions in each category.

        The key is the category name
        and the value is the no of questions
        """
        categories = Category.objects.all()
        question_count_category_dict = {}
        for category in categories:
            question_count_category_dict.setdefault(
                category.name, category.questions.count()
            )
        return question_count_category_dict


class Question(models.Model):
    question = models.TextField()
    difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES, max_length=100, db_index=True
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=100, db_index=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="questions"
    )
    correct_answer = models.CharField(max_length=200)
    explanation = models.CharField(max_length=1000, blank=True)
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="questions_verified",
        blank=True,
    )
    image = models.ImageField(blank=True, upload_to="quiz/")
    category = models.ForeignKey(
        Category, on_delete=models.SET(get_sentinel_category), related_name="questions"
    )
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = models.Manager()
    verified = VerifiedManager()
    unverified = UnVerifiedManager()

    def __str__(self):
        return self.question

    def clean(self):
        """validate the verification of a question"""
        if self.is_verified and self.verified_by is None:
            raise ValidationError("Add a user to verified_by")
        if self.verified_by and not self.is_verified:
            raise ValidationError("is_verified needs to be updated")
        if self.verified_by and self.is_verified and not self.date_verified:
            raise ValidationError("date_verified needs to be updated")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @staticmethod
    def last_created() -> datetime.datetime:
        """
        returns the time and date of the most recent created question.
        """
        return Question.objects.order_by("-date_created").first().date_created

    @staticmethod
    def last_verified() -> datetime.datetime:
        return (
            Question.objects.filter(is_verified=True)
            .order_by("-date_verified")
            .first()
            .date_verified
        )

    @staticmethod
    def no_of_all_questions() -> int:
        return Question.objects.count()

    @staticmethod
    def no_of_verified_questions() -> int:
        return Question.verified.count()

    @staticmethod
    def no_of_unverified_questions() -> int:
        return Question.unverified.count()

    @staticmethod
    def no_of_easy_questions() -> int:
        return Question.objects.filter(difficulty="easy").count()

    @staticmethod
    def no_of_medium_questions() -> int:
        return Question.objects.filter(difficulty="medium").count()

    @staticmethod
    def no_of_hard_questions() -> int:
        return Question.objects.filter(difficulty="hard").count()

    def verify(self, user: User):
        self.is_verified = True
        self.date_verified = timezone.now()
        self.verified_by = user
        self.save()

    def unverify(self):
        self.is_verified = False
        self.date_verified = None
        self.verified_by = None
        self.save()


class InCorrectAnswer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="incorrect_answers"
    )
    option = models.CharField(max_length=1000)

    def __str__(self):
        return self.option

    def clean(self):
        """validate that true/false question has only one incorrect answer"""
        if (
            self.question.type == "True / False"
            and self.question.incorrect_answers.count() >= 1
        ):
            if (
                self.id is None
            ):  # ensures that editing old question don't raise this error
                raise ValidationError(
                    "True/False questions can have only one \
                incorrect answer"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
