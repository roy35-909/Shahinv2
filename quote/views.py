
from rest_framework.response import Response
from rest_framework.views import APIView
from shahin.base import NewAPIView
from .models import UserSchedule
from .utils import schedule_user_notifications
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated

class UserScheduleAPIView(APIView):
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