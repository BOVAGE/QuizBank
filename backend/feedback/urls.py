from django.urls import path

from .views import FeedbackDetailView, FeedbackListView

app_name = "feedback"
urlpatterns = [
    path('', FeedbackListView.as_view(), name="feedback-list"),
    path('<int:id>', FeedbackDetailView.as_view(), name="feedback-detail"),
]
