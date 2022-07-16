from django.urls import path
from .views import QuestionListCreateView

urlpatterns = [
    path('', QuestionListCreateView, name='question-list'),
]