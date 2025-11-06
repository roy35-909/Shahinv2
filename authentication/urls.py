from django.urls import include, path
from .views import UserRegisterAPIView,ForgotPasswordAPIView,VerifyOtpAPIView,ResetPasswordAPIView,AddTargetAPIView,CustomTokenObtainPairView,DeviceRegisterView,GoogleLogin, AppleLoginView, GoogleLoginAPIView
urlpatterns = [
    # Authentication Paths
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('sauth/',include('djoser.urls')),
    # path('sauth/',include('djoser.urls.jwt')),
    # path('sauth/',include('djoser.social.urls')),
    # path('sauth/',include('djoser.social.urls')),
    # path('accounts/', include('allauth.urls')),
    # path('api/google/login/', GoogleLogin.as_view(), name='google_login'),
    path('user_registration/', UserRegisterAPIView.as_view(), name="User Registration API View"),
    path('forget_passord', ForgotPasswordAPIView.as_view(), name="Forget Password API View"),
    path('veryfy_otp/', VerifyOtpAPIView.as_view(), name="Verify The OTP View"),
    path('reset_password/', ResetPasswordAPIView.as_view(), name="Verify The OTP View"),
    path('add_target/', AddTargetAPIView.as_view(), name="Add Target To User"),
    path('register_fcm',DeviceRegisterView.as_view(), name="Add FCM Token"),
    # path('apple_login/', AppleLoginView.as_view(), name="Apple Login API View"),
    path('auth/', GoogleLoginAPIView.as_view(), name="Google Login API View"),
]