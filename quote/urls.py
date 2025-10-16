from django.urls import include, path

from .views import UserScheduleAPIView
urlpatterns = [

    path('create_schedule', UserScheduleAPIView.as_view(), name="User Schedule API View")
]