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
from django.shortcuts import get_object_or_404
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
        if badge.points_required <= user.points:
            # percentage = 100
            # if badge.name == 'Tracker':
            #     # percentage = has_logged_in_seven_consecutive_days(user)
            #     # percentage = min(percentage,100)
            #     if percentage <100:
            #         return Response({"error":"User Not Able To Unlock This Badge"}, status=status.HTTP_400_BAD_REQUEST)
            # if badge.name == 'Hunter':
            #     percentage= has_share_10_quote_on_social_media(user)
            #     if percentage <100:
            #         return Response({"error":"User Not Able To Unlock This Badge"}, status=status.HTTP_400_BAD_REQUEST)

            user_badge,created = UserBadge.objects.get_or_create(user=user,badge=badge)
            user_badge.is_completed = True
            user_badge.save()
            return Response({"success":f"{user_badge.badge.name} Badge Unlocked"}, status=status.HTTP_200_OK)
        else:
            return Response({"error":"User Not Able To Unlock This Badge"}, status=status.HTTP_400_BAD_REQUEST)
        

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
        send_notification_to_tokens(tokens=["fWXiqUZsbE0buJbxdy22-H:APA91bGi-Dlo6PT4eLl6OK6AuP2U3rM8czVFm6evxPOGsV-_e39HZSCc95yjG4RGUa7DfX_ZmWCXUH_fHZavJc9nYSlHdD86NLMOiCeJ31ekrtx7nZ4acmE",], title="This Is the Final Test", body="Hello World! This is a test notification from Shahin App.")
        # from payment.tasks import expire_subscription
        # expire_subscription.apply_async(args=[request.user.id], countdown=10)
        return Response({'msg':'success'}, status=status.HTTP_200_OK)
    

class DeleteUserAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users

    def delete(self, request, user_id=None):
        """
        Delete a user by ID.
        - If user_id is None, deletes the logged-in user
        - Admins can delete any user by providing user_id
        """
        if user_id:
            # Only admin can delete other users
            if not request.user.is_staff:
                return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            user = get_object_or_404(User, id=user_id)
        else:
            # Delete logged-in user
            user = request.user

        user.delete()
        return Response({"detail": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)