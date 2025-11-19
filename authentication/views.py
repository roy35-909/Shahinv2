import random
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import uuid
from rest_framework.response import Response
from rest_framework import status
from shahin.base import *
from shahin.response import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserBadge,Badge
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import LoginHistory, Device 
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client   
from rest_framework.authtoken.models import Token


from .utils import verify_apple_token,verify_firebase_token                   
def send_otp_email(user_email, otp_code):
    subject = "Reset Your Password - MP"
    from_email = settings.EMAIL_HOST_USER


    context = {
        "otp_code": otp_code
    }
    html_content = render_to_string("email_body.html", context)
    text_content = strip_tags(html_content) 

    email = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


class UserRegisterAPIView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewUserRegisterSerializer
    def post(self, request):
        '''
            **This API is for User Registration.** \n
            After Creating User It Will Give 201 User Created Response.

            Required Fields:\n
                1) first_name\n
                2) email\n
                4) password\n
            \n
            Thank You

        '''
        data = request.data
        first_name = data.get("first_name")
        email = data.get("email")

        password = data.get("password")

        if not all([first_name, email,password]):
            return s_406("All Field ")
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(
            username=email,   
            first_name=first_name,
            email=email,
        )
        refresh = RefreshToken.for_user(user)
        user.set_password(password)  
        user.save()
        badges = Badge.objects.all()
        for badge in badges:
            UserBadge.objects.get_or_create(user=user, badge=badge)
        return Response({
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "email": user.email,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    

class ForgotPasswordAPIView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        '''
            **This API is for Get The OTP when User Will Click On Forget Password and Provide his Email** \n
            It will Send An Email with OTP.

            Required Fields:\n
                1) email\n
            \n
            Thank You

        '''
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


            otp = str(random.randint(1000, 9999))
            user.otp = otp
            user.save()


            send_otp_email(
                user_email=email,
                otp_code = otp
            )

            return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GoogleAuthView(APIView):
#     def post(self, request):
#         token = request.data.get("id_token")
#         if not token:
#             return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
#             email = idinfo.get("email")
#             name = idinfo.get("name")
#             google_id = idinfo.get("sub")
#             if not email:
#                 return Response({"error": "Email not found in Google response"}, status=status.HTTP_400_BAD_REQUEST)
#             user, created = User.objects.get_or_create(
#                 email=email,
#                 defaults={"username": email.split("@")[0], "first_name": name}
#             )
#             from rest_framework_simplejwt.tokens import RefreshToken
#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#                 "email": email,
#                 "new_user": created
#             })
#         except ValueError:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)



class VerifyOtpAPIView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOtpSerializer
    def post(self, request):
        '''
            **This API is for Verify The OTP , It will Provide You A reset_token what you need in the next Phase** \n
            It Will Return A Reset Token , And Success Message.

            Required Fields:\n
                1) email\n
                2) otp\n
            \n
            Thank You

        '''
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.otp == otp:
                reset_token = uuid.uuid4()
                user.password_forget_token = reset_token
                user.otp = None  # clear OTP once verified
                user.save()
                return Response({"message": "OTP verified successfully", "reset_token":f"{reset_token}"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class ResetPasswordAPIView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        '''
            **After Verifying The OTP , You Get A Reset Token . Now This API will take the token and Reset The Password** \n
            You Need To Provide new password with the reset_token.

            Required Fields:\n
                1) email\n
                2) reset_token\n
                3) password\n
                4) retype_password\n
            \n
            Thank You
        '''
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            reset_token = serializer.validated_data["reset_token"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email, password_forget_token=reset_token)
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid email or reset token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


            user.set_password(password)
            user.password_forget_token = None 
            user.save()

            return Response(
                {"message": "Password reset successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddTargetAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTargetSerializer
    def post(self, request):
        """
        **Add or Update User Targets**
        User can select multiple targets: Fitness, Career, Business, Discipline, Mindset
        """
        user = request.user
        serializer = UserTargetSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Targets updated successfully", "targets": serializer.data['target']},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Call the parent class's post method to get the token response
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Extract the user from the JWT token payload
            access_token = response.data.get('access')
            if access_token:
                # Decode the access token and retrieve the user ID from the payload
                from rest_framework_simplejwt.tokens import AccessToken
                try:
                    token = AccessToken(access_token)
                    user_id = token['user_id']  # The 'user_id' key corresponds to the authenticated user
                    user = self.get_user(user_id)  # Get the user object
                    if user:
                        # Log the successful login
                        LoginHistory.objects.create(user=user)
                except Exception as e:
                    print(f"Error retrieving user from token: {e}")
        
        return response

    def get_user(self, user_id):
        """Helper method to get a user object by ID."""
        try:
            from django.contrib.auth import get_user_model
            return get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return None
        


class DeviceRegisterView(NewAPIView):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        device, _ = Device.objects.get_or_create(user=request.user,token = data['token'])
        ser = DeviceSerializer(device)
        return Response(ser.data, status=status.HTTP_200_OK)
    



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:8000/accounts/google/login/callback/"


class AppleLoginView(NewAPIView):
    serializer_class = AppleLoginSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        identity_token = request.data.get("identity_token")
        if not identity_token:
            return Response({"error": "Missing identity_token"}, status=400)

        try:
            decoded = verify_apple_token(identity_token)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        email = decoded.get("email")
        apple_user_id = decoded.get("sub")

        user, created = User.objects.get_or_create(
            defaults={"email": email or f"{apple_user_id}@apple.com"},
            first_name = request.data.get("full_name","Apple User"),
        )
        token = RefreshToken.for_user(user)


        return Response({
            "access": token.acess_token,
            "user": {"id": user.id, "email": user.email}
        }, status=200)
    

# class GoogleLoginAPIView(NewAPIView):
#     """
#     POST /auth/google/
#     {
#         "identity_token": "<id_token_from_flutter>"
#     }
#     """
#     serializer_class = GoogleLoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = GoogleLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         identity_token = serializer.validated_data["idToken"]
#         print(identity_token)
#         decoded = verify_firebase_token(identity_token)
#         if not decoded:
#             return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
#         uid = decoded["uid"]
#         email = decoded.get("email")
#         provider = decoded.get("firebase", {}).get("sign_in_provider")

#         user, _ = User.objects.get_or_create(email=email, defaults={"username": uid})
#         token = RefreshToken.for_user(user)

#         return Response({
#             "access": str(token.access_token),
#             "refresh": str(token)
#         })
    
class GoogleLoginAPIView(APIView):
    """
    POST /auth/google/ OR /auth/apple/
    Payload:
    {
        "idToken": "<firebase_id_token>",
        "provider": "google.com" | "apple.com"
    }
    """
    serializer_class = GoogleLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token_value = serializer.validated_data["idToken"]
        provider = serializer.validated_data["provider"].lower()

        # Verify Firebase ID token
        if provider in ["apple.com", "apple"]:
            email = serializer.validated_data.get("email")
            provider_name = "apple.com"
        else:
            decoded = verify_firebase_token(id_token_value)
            if not decoded:
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

            uid = decoded["uid"]
            email = decoded.get("email")
            provider_name = decoded.get("firebase", {}).get("sign_in_provider")

        # Create or get user
        user, _ = User.objects.get_or_create(email=email)
        token = RefreshToken.for_user(user)
        print(provider_name)
        return Response({
            "access": str(token.access_token),
            "refresh": str(token),
        })