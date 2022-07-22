from authentication.views import UserListView, UserStaff
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from quiz.views import (CategoryDetailView, CategoryListCreateView,
                        StatisticsView, UserQuestionListView,
                        UserQuestionStatView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/questions/', include('quiz.urls')),
    path('api/v1/feedback/', include('feedback.urls')),
    path('api/v1/statistics/', StatisticsView, name="statistics"),
    path('api/v1/categories/', CategoryListCreateView, name="categories-list"),
    path('api/v1/categories/<slug:slug>', CategoryDetailView, name="categories-detail"),
    path('api/v1/users', UserListView.as_view(), name="user-list"),
    path('api/v1/users/<int:id>/staff', UserStaff.as_view(), name="user-staff"),
    path('api/v1/users/<int:id>/questions', UserQuestionListView, name="user-question"),
    path('api/v1/users/<int:id>/questions-stat', UserQuestionStatView, name="user-question-stat"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 ='common.errors.not_found'
handler500 = 'common.errors.server'
