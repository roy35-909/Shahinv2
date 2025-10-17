from django.urls import include, path
from .views import (
    UserBadgeListAPIView,
    UnloackABadge,
    UserProfilePhotoUpdateAPIView,
    UserUpdateAPIView,
    GetUserProfileAPIView,
    ChangePasswordAPIView,
    SupportCreateAPIView,
    GetUserPoints,
)

urlpatterns = [
    path('user/badges/',UserBadgeListAPIView.as_view(), name="User Badges List"),
    path('user/badge/unlock/<int:pk>/',UnloackABadge.as_view(), name="Unlock New Badge"),
        path("profile/photo/", UserProfilePhotoUpdateAPIView.as_view(), name="user-profile-photo"),
    path("profile/update",UserUpdateAPIView.as_view(), name="Profile Update"),
    path("profile/get", GetUserProfileAPIView.as_view(), name="Get User Profile"),
    path("auth/change_password",ChangePasswordAPIView.as_view(), name="Change Password View"),
    path("user/support/",SupportCreateAPIView.as_view(),name="User Support Create API View"),
    path("user/total_points/",GetUserPoints.as_view(), name="User Total Points")
]