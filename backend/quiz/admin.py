from django.contrib import admin
from .models import Category, Question, InCorrectAnswer


class InCorrectAnswerInline(admin.StackedInline):
    model = InCorrectAnswer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    list_filter = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question", "difficulty", "type", "is_verified", "category"]
    list_filter = ["question", "difficulty", "type", "is_verified", "category"]
    search_fields = ["question", "difficulty", "type", "is_verified", "category"]
    inlines = [InCorrectAnswerInline]


@admin.register(InCorrectAnswer)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question", "option"]
    list_filter = ["question"]
