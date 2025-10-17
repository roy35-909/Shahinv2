
from rest_framework.response import Response
from rest_framework.views import APIView
from shahin.base import NewAPIView
from .models import UserSchedule
from .utils import schedule_user_notifications
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from shahin.response import *
from django.core.exceptions import ObjectDoesNotExist
class UserScheduleAPIView(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserScheduleSerializer
    def post(self, request):
        # Deserialize the request data using the serializer
        serializer = UserScheduleSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']
            interval_minutes = serializer.validated_data['interval_minutes']

            # Update or create the user schedule
            schedule, created = UserSchedule.objects.get_or_create(user=user)
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.interval_minutes = interval_minutes
            schedule.save()

            # Schedule notifications for the user
            schedule_user_notifications(user)

            return Response({"message": "Schedule updated successfully"})
        
        return Response(serializer.errors)
    
class ListUserQuoteHistory(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer

    def get(self, request):
        user = request.user
        history = UserQuote.objects.filter(user=user).order_by('-id')

        ser = UserHistorySerializer(history, many=True)
        return s_200(ser)
    


class LikedUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except(ObjectDoesNotExist):
            return s_404("UserQuote")
        
        if user_quote.is_liked:
            pass
        else:
            user.points+=1
            user.save()
        user_quote.is_liked = True

        user_quote.save()
        
        return Response({"success":"User Liked Saved"},status.HTTP_200_OK)
    
class SavedUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except(ObjectDoesNotExist):
            return s_404("UserQuote")
        
        user_quote.is_saved = True
        user_quote.save()

        return Response({"success":"User Quote Saved"},status.HTTP_200_OK)
    
class ShareUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except(ObjectDoesNotExist):
            return s_404("UserQuote")
        
        user_quote.is_share = True
        user_quote.save()

        return Response({"success":"User Quote Shared"},status.HTTP_200_OK)

class GetSavedUserQuote(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer
    def get(self,request):
        user = request.user


        user_quote = UserQuote.objects.filter(user=user,is_saved=True)
        ser = UserHistorySerializer(user_quote,many=True)
        return s_200(ser)
    
class GetLikedUserQuote(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer
    def get(self,request):
        user = request.user


        user_quote = UserQuote.objects.filter(user=user,is_liked=True)
        ser = UserHistorySerializer(user_quote,many=True)
        return s_200(ser)
