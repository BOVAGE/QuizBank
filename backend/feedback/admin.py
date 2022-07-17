from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "created_by", "resolved_by"]
    list_filter = ["question", "created_by", "resolved_by"]
