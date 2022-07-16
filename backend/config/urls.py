from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from quiz.views import StatisticsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/questions/', include('quiz.urls')),
    path('api/v1/statistics/', StatisticsView, name="statistics"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
