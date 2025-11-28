
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from shahin.base import NewAPIView
from .models import UserPointHistory, UserSchedule
from .utils import schedule_user_notifications
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from shahin.response import *
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.pagination import PageNumberPagination

class QuotePagination(PageNumberPagination):
    page_size = 10  # You can adjust this value based on your preference
    page_size_query_param = 'page_size'  # Allow the client to specify page size
    max_page_size = 100  # Set a maximum page size


class QuoteListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user  
        user_targets = user.target
        if not user_targets:
            return Response({"error": "User has no target categories defined."}, status=status.HTTP_400_BAD_REQUEST)
        quotes = Quote.objects.filter(category__in=user_targets)
        user_quote_ids = UserQuote.objects.filter(user=user,is_viewed=True).values_list('quote_id', flat=True)
        user_quote_ids_today = UserQuote.objects.filter(
        user=user,
        sent_at__date=timezone.now().date()
    ).values_list('quote_id', flat=True)
        print(f"Today's viewed quotes: {len(user_quote_ids_today)}")
        if user.subscription_type == 'free':
            if len(user_quote_ids_today) >= 5:
                quotes = []
            else:
                quotes = quotes.exclude(id__in=user_quote_ids)[:5]
        else:
            quotes = quotes.exclude(id__in=user_quote_ids)
        paginator = QuotePagination()
        paginated_quotes = paginator.paginate_queryset(quotes, request)
        user_quote_list = []
        for quote in paginated_quotes:
            user_quote, created = UserQuote.objects.get_or_create(user=user, quote=quote)
            user_quote_list.append(user_quote)
        serializer = UserHistorySerializer(user_quote_list, many=True)

        return paginator.get_paginated_response(serializer.data)


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


            schedule, created = UserSchedule.objects.get_or_create(user=user)
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.interval_minutes = interval_minutes
            schedule.save()


            schedule_user_notifications(user)

            return Response({"message": "Schedule updated successfully"})
        
        return Response(serializer.errors)
    
class ListUserQuoteHistory(NewAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserHistorySerializer

    def get(self, request):
        user = request.user
        history = UserQuote.objects.filter(user=user,is_liked=True).order_by('-id')

        ser = UserHistorySerializer(history, many=True)
        return s_200(ser)
    


class LikedUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except ObjectDoesNotExist:
            return s_404("UserQuote")

        if user_quote.is_liked:
            # Unlike Action ➝ Decrease points
            user_quote.is_liked = False
            user_quote.save()

            user.points -= 1
            user.save()

            UserPointHistory.objects.create(
                user=user,
                points_changed=-1,
                reason="Unliked a quote"
            )

        else:
            # Like Action ➝ Increase points
            user_quote.is_liked = True
            user_quote.save()

            user.points += 1
            user.save()

            UserPointHistory.objects.create(
                user=user,
                points_changed=+1,
                reason="Liked a quote"
            )

        return Response({"success": "User Liked Saved"}, status=status.HTTP_200_OK)
    

    
class DeleteUserQuote(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except(ObjectDoesNotExist):
            return s_404("UserQuote")
        
        user_quote.delete()

        return Response({"success":"User Quote Deleted"},status.HTTP_200_OK)
    
class SavedUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except ObjectDoesNotExist:
            return s_404("UserQuote")

        if user_quote.is_saved:
            # Undo save ➝ -1 point
            user_quote.is_saved = False
            user_quote.save()
            user.points -= 1
            user.save()

            UserPointHistory.objects.create(
                user=user,
                points_changed=-1,
                reason="Removed saved quote"
            )
        else:
            # Save ➝ +1 point
            user_quote.is_saved = True
            user_quote.save()
            user.points += 1
            user.save()

            UserPointHistory.objects.create(
                user=user,
                points_changed=+1,
                reason="Saved a quote"
            )

        return Response({"success": "User Quote Saved"}, status=status.HTTP_200_OK)
    

class ViewedUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except ObjectDoesNotExist:
            return s_404("UserQuote")
        
        if not user_quote.is_viewed:
            user_quote.is_viewed = True
            user_quote.save()

            user.points += 1
            user.save()

            UserPointHistory.objects.create(
                user=user,
                points_changed=+1,
                reason="Viewed a quote"
            )

        return Response({"success": "User Viewed The Quote"}, status=status.HTTP_200_OK)
    
class ShareUserQuote(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user

        try:
            user_quote = UserQuote.objects.get(id=pk, user=user)
        except ObjectDoesNotExist:
            return s_404("UserQuote")
        
        if not user_quote.is_share:
            user_quote.is_share = True
            user_quote.save()

            user.points += 25
            user.save()

            UserPointHistory.objects.create(
                user=user,
                points_changed=+25,
                reason="Shared a quote"
            )

        return Response({"success": "User Quote Shared"}, status=status.HTTP_200_OK)
    


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
