from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from .views import UserRegisterAPIView,ForgotPasswordAPIView,VerifyOtpAPIView,ResetPasswordAPIView,AddTargetAPIView
urlpatterns = [
    # Authentication Paths
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('sauth/',include('djoser.urls')),
    # path('sauth/',include('djoser.urls.jwt')),
    path('sauth/',include('djoser.social.urls')),
    path('sauth/',include('djoser.social.urls')),
    path('user_registration/', UserRegisterAPIView.as_view(), name="User Registration API View"),
    path('forget_passord', ForgotPasswordAPIView.as_view(), name="Forget Password API View"),
    path('veryfy_otp/', VerifyOtpAPIView.as_view(), name="Verify The OTP View"),
    path('reset_password/', ResetPasswordAPIView.as_view(), name="Verify The OTP View"),
    path('add_target/', AddTargetAPIView.as_view(), name="Add Target To User")
]