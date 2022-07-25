from django.urls import path

from .views import (QuestionDetailView, QuestionListCreateView,
                    QuestionListFullView, QuestionVerification,
                    UnverifiedQuestionListFullView)
app_name = "quiz"
urlpatterns = [
    path('', QuestionListCreateView, name='question-list'),
    path('<int:id>', QuestionDetailView, name='question-detail'),
    path('full', QuestionListFullView, name='question-list-full'),
    path('unverified', UnverifiedQuestionListFullView, 
    name='unverified-question-list-full'),
    path('<int:id>/verification', QuestionVerification, 
    name='question-verification'),
]
