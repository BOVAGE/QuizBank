from django.contrib.auth import get_user_model
from django.db import models
from quiz.models import Question

User = get_user_model()


class Feedback(models.Model):
    question = models.ForeignKey(
        Question, related_name="feedbacks", on_delete=models.CASCADE
    )
    issue = models.CharField(max_length=1000)
    explanation = models.CharField(max_length=1000)
    created_by = models.ForeignKey(
        User, related_name="feedbacks", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, related_name="resolved_feedbacks", null=True, on_delete=models.SET_NULL
    )
    date_resolved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.issue[:15]
