from django.urls import path

from .views import (QuestionListCreateView, QuestionListFullView,
                    QuestionVerification, UnverifiedQuestionListFullView)

urlpatterns = [
    path('', QuestionListCreateView, name='question-list'),
    path('full', QuestionListFullView, name='question-list-full'),
    path('unverified', UnverifiedQuestionListFullView, 
    name='unverified-question-list-full'),
    path('<int:id>/verification', QuestionVerification, 
    name='question-verification'),
]
