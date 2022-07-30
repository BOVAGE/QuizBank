from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    bio = models.CharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatar/", default="avatar.jpg", blank=True)

    def get_tokens_for_user(self):
        refresh = RefreshToken.for_user(self)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def total_user() -> int:
        return User.objects.count()

    @staticmethod
    def total_staff() -> int:
        return User.objects.filter(is_staff=True).count()

    def get_number_of_questions(self) -> int:
        return self.questions.count()

    def get_number_of_verified_questions(self) -> int:
        return self.questions.filter(is_verified=True).count()

    def get_number_of_unverified_questions(self) -> int:
        return self.questions.filter(is_verified=False).count()
