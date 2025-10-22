from rest_framework.response import Response
from rest_framework.views import APIView
from shahin.base import NewAPIView

from .utils import *
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from shahin.response import *
from django.core.exceptions import ObjectDoesNotExist
from ai.tasks import generate_quote
from authentication.models import UserBadge
from shahin.firebase_utils import send_notification_to_tokens
class UserBadgeListAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBadgeSerializer
    def get(self, request):

        user = request.user

        user_badges = UserBadge.objects.filter(user=user)
        serializer = UserBadgeSerializer(user_badges, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UnloackABadge(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,pk):
        user = request.user
        try:
            badge = Badge.objects.get(id=pk)
        except(ObjectDoesNotExist):
            return s_404("Badge")
        if badge.points_required >= user.points:

            if badge.name == 'Tracker':
                percentage = has_logged_in_seven_consecutive_days(user)
                percentage = min(percentage,100)
                if percentage <100:
                    return Response({"error":"User Not Able To Unlock This Badge"})
            if badge.name == 'Hunter':
                percentage= has_share_10_quote_on_social_media(user)
                if percentage <100:
                    return Response({"error":"User Not Able To Unlock This Badge"})

            user_badge,created = UserBadge.objects.get_or_create(user=user,badge=badge)
            user_badge.is_completed = True
            user_badge.save()
            return Response({"success":f"{user_badge.badge.name} Badge Unlocked"})
        

class UserProfilePhotoUpdateAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfilePhotoSerializer
    def put(self, request):
        serializer = UserProfilePhotoSerializer(
            request.user, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile photo updated successfully", "photo": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

## Duplicate Support API View
class UserUpdateAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        # Check email uniqueness
        new_email = data.get("email")
        if new_email and User.objects.exclude(pk=user.pk).filter(email=new_email).exists():
            return Response({"email": "This email is already taken."}, status=status.HTTP_400_BAD_REQUEST)

        # Partial update with serializer (no validation logic here)
        serializer = UserUpdateSerializer(user, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully", "user": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class UserUpdateAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    def put(self, request):
        """Update logged-in user profile"""
        user = request.user
        data = request.data.copy()

        # 🔹 Remove empty fields so they won't overwrite
        for field in list(data.keys()):
            if data[field] in ["", None, "null"]:
                data.pop(field)

        # 🔹 Check email uniqueness
        new_email = data.get("email")
        if new_email and User.objects.exclude(pk=user.pk).filter(email=new_email).exists():
            return Response({"email": "This email is already taken."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserUpdateSerializer(user, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully", "user": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetUserProfileAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get(self, request):
        """Get logged-in user profile"""
        serializer = UserUpdateSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChangePasswordAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]
        retype_password = serializer.validated_data["retype_password"]
        if not user.check_password(old_password):
            return Response({"old_password": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != retype_password:
            return Response({"new_password": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        if old_password == new_password:
            return Response({"new_password": "New password cannot be same as old password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
    
# Create support entry
class SupportCreateAPIView(NewAPIView):
    permission_classes = [AllowAny]
    serializer_class = SupportSerializer
    def post(self, request, *args, **kwargs):
        serializer = SupportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetUserPoints(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        return Response({'points':user.points}, status=status.HTTP_200_OK)
    
class PrintQuote(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # result = generate_quote.delay('Fitness')
        send_notification_to_tokens(tokens=["d06EoZyuqE0t5aqPEbDBdt:APA91bHwMloHiRgtw3KL7S6G_vDPKI-t-D4Eq_5B7tHkh4MPuoRbTQ6jQ5RgZxEdiHjYtQSBUrZZ8bW7n3fAunLnv8weWF8C-LN6FG9vkynrCDjg3iMvwp0",], title="Testing My Token", body="Hello From Roy")
        return Response({'msg':'success'}, status=status.HTTP_200_OK)
    
    