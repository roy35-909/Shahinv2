from authentication.models import Friendship
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from shahin.base import NewAPIView
from django.db.models import Q
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from quote.models import UserQuote
from authentication.models import UserBadge
User = get_user_model()

class SendFriendRequestAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SendFriendRequestSerializer

    def post(self, request, *args, **kwargs):
        user1 = request.user
        user2_id = request.data.get('user2_id')


        try:
            user2 = User.objects.get(id=user2_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


        friendship = Friendship.objects.filter(
            Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
        ).first()

        if friendship:

            if friendship.status == Friendship.ACCEPTED:
                return Response({'detail': 'You are already friends.', 'status': 'friends'}, status=status.HTTP_400_BAD_REQUEST)

     
            if friendship.status == Friendship.PENDING and friendship.user1 == user1:
                return Response({'detail': 'Friend request already sent.', 'status': 'request-sent'}, status=status.HTTP_400_BAD_REQUEST)


            if friendship.status == Friendship.PENDING and friendship.user1 == user2:
                return Response({'detail': 'User has already sent you a friend request.', 'status': 'request-received'}, status=status.HTTP_400_BAD_REQUEST)


            return Response({'detail': f'Cannot send request. Status: {friendship.status}'}, status=status.HTTP_400_BAD_REQUEST)


        friendship = Friendship.objects.create(user1=user1, user2=user2, status=Friendship.PENDING)
        friendship.send_request()  

        return Response({
            'friendship_id': friendship.id,
            'first_name': friendship.user2.first_name,
            'profile_photo': request.build_absolute_uri(friendship.user2.profile_photo.url) if friendship.user2.profile_photo else None,
            'points': friendship.user2.points,
            'status': 'request-sent'
        }, status=status.HTTP_201_CREATED)


class AcceptFriendRequestAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AcceptFriendRequestSerializer
    def post(self, request, *args, **kwargs):
        user = request.user  # Current authenticated user
        friendship_id = request.data.get('friendship_id')

        try:
            friendship = Friendship.objects.get(id=friendship_id)
        except Friendship.DoesNotExist:
            return Response({'detail': 'Friendship not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the request is for the authenticated user and it's pending
        if friendship.user2 != user or friendship.status != Friendship.PENDING:
            return Response({'detail': 'Friend request is not valid for this user or already accepted/rejected.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Accept the friend request
        friendship.accept_request()
        return Response({
        'friendship_id':friendship.id, 
        'first_name':friendship.user2.first_name, 
        'profile_photo':request.build_absolute_uri(friendship.user2.profile_photo.url) if friendship.user2.profile_photo else None, 
        'points':friendship.user2.points, 
        'status':'friends'}, 
        status=status.HTTP_200_OK)


class ListFriendRequestsAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendshipSerializer
    def get(self, request, *args, **kwargs):
        user = request.user
        # Get all pending requests for this user (requests they are receiving)
        pending_requests = Friendship.objects.filter(user2=user, status=Friendship.PENDING)
        serializer = ListFriendRequestSerializer(pending_requests, many=True, context = {'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CancelFriendRequestAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AcceptFriendRequestSerializer
    def post(self, request, *args, **kwargs):
        user = request.user  # Current authenticated user

        friendship_id = request.data.get('friendship_id')

        try:
            friendship = Friendship.objects.get(id=friendship_id)
        except Friendship.DoesNotExist:
            return Response({'detail': 'Friendship not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the request is for the authenticated user and it's pending
        if friendship.user1 != user or friendship.status != Friendship.PENDING:
            return Response({'detail': 'Friend request is not pending or cannot be canceled by this user.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Cancel the request (delete the friendship)
        friendship.cancel_request()
        return Response({'detail': 'Friend request canceled.'}, status=status.HTTP_200_OK)
    
class RejectFriendRequestAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AcceptFriendRequestSerializer

    def post(self, request, *args, **kwargs):
        user = request.user  # current authenticated user
        friendship_id = request.data.get('friendship_id')

        try:
            friendship = Friendship.objects.get(id=friendship_id)
        except Friendship.DoesNotExist:
            return Response({'detail': 'Friendship not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if this user is the receiver of the friend request
        if friendship.user2 != user or friendship.status != Friendship.PENDING:
            return Response(
                {'detail': 'Friend request cannot be rejected by this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reject means deleting the friendship object
        friendship.delete()

        return Response({'detail': 'Friend request rejected and removed.'}, status=status.HTTP_200_OK)


class ListFriendsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Query the Friendship model to get all accepted friendships for the current user
        friendships = Friendship.objects.filter(
            Q(user1=user) | Q(user2=user),  # Check both user1 and user2 sides of the relationship
            status='accepted'  # Only get accepted friendships
        )
        
        # Prepare the list of friends (user1 or user2, excluding the current user)
        friends = []
        for friendship in friendships:
            if friendship.user1 != user:
                friends.append(friendship.user1)
            else:
                friends.append(friendship.user2)
        
        # Serialize the friends data to send back in the response
        friends_data = [{'id': friend.id, 'email': friend.email, 'profile_photo': friend.profile_photo.url if friend.profile_photo else None} for friend in friends]
        
        return Response(friends_data, status=status.HTTP_200_OK)
    

class SearchUserAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSearchSerializer
    def get(self, request, *args, **kwargs):
        '''
        Example Request:
            GET friends/search/?q=john
        '''
        search_term = request.query_params.get('q', '').strip()  # 'q' is the search query parameter

        if not search_term:
            return Response({'detail': 'Please provide a search term.'}, status=status.HTTP_400_BAD_REQUEST)
        if (search_term.startswith('"') and search_term.endswith('"')) or \
           (search_term.startswith("'") and search_term.endswith("'")):
            search_term = search_term[1:-1].strip()

        print(search_term)
        # Perform a case-insensitive search on both the username (name) and email fields
        users = User.objects.filter(
            Q(first_name__icontains=search_term) |
            Q(email__icontains=search_term)
        ).exclude(id=request.user.id)

        if users.exists():
            serializer = UserSearchSerializer(users, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No users found matching the search criteria.'}, status=status.HTTP_404_NOT_FOUND)
        



class LeaderboardAPIView(NewAPIView):
    """
    Leaderboard API with badges.
    Shows weekly, monthly, and all-time top users
    based on their total activity from UserQuote.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaderboardUserSerializer

    def get(self, request):
        now = timezone.now()
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        def build_leaderboard(time_filter=None):
            queryset = UserQuote.objects.select_related("user")

            if time_filter:
                queryset = queryset.filter(sent_at__gte=time_filter)

            leaderboard = (
                queryset
                .values("user")
                .annotate(total_points=Count("id"))
                .order_by("-total_points")[:10]
            )

            # Get all user objects for the leaderboard
            user_ids = [item["user"] for item in leaderboard]
            users = User.objects.filter(id__in=user_ids)
            user_map = {u.id: u for u in users}

            results = []
            for index, item in enumerate(leaderboard, start=1):
                user_obj = user_map.get(item["user"])
                if not user_obj:
                    continue

                total_points = item["total_points"]
                user_badge = (
                    UserBadge.objects.filter(user=user_obj, is_completed=True)
                    .order_by("-id")
                    .first()
                )

                results.append({
                    "user_id": user_obj.id,
                    "first_name": user_obj.first_name,
                    "profile_photo": (
                        request.build_absolute_uri(user_obj.profile_photo.url)
                        if user_obj.profile_photo else None
                    ),
                    "subscription_type": getattr(user_obj, "subscription_type", "free"),
                    "total_points": total_points,
                    "level": total_points / 20,
                    "rank": index,
                    "badge": {
                        "badge_id": user_badge.badge.id if user_badge else None,
                        "badge_name": user_badge.badge.name if user_badge else None,
                        "is_completed": user_badge.is_completed if user_badge else False,
                        "image": (
                            request.build_absolute_uri(user_badge.badge.image.url)
                            if (user_badge and user_badge.badge and user_badge.badge.image)
                            else None
                        )
                    },
                })

            return results

        data = {
            "weekly": build_leaderboard(week_start),
            "monthly": build_leaderboard(month_start),
            "all_time": build_leaderboard(),
        }

        return Response(data)


class FriendLeaderboardAPIView(APIView):
    """
    Leaderboard among the authenticated user's friends (including self).
    Always shows the current user's activity even if others have none.
    """

    def get(self, request):
        user = request.user
        now = timezone.now()
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        # --- Step 1: Find accepted friends ---
        friend_ids = Friendship.objects.filter(
            Q(user1=user, status=Friendship.ACCEPTED)
            | Q(user2=user, status=Friendship.ACCEPTED)
        ).values_list("user1", "user2")

        friend_ids = {uid for pair in friend_ids for uid in pair if uid != user.id}
        friend_ids.add(user.id)  # Always include self

        # --- Step 2: Helper to build leaderboard ---
        def build_leaderboard(time_filter=None):
            queryset = UserQuote.objects.filter(user_id__in=friend_ids)
            if time_filter:
                queryset = queryset.filter(sent_at__gte=time_filter)

            leaderboard = (
                queryset.values(
                    "user__id",
                    "user__first_name",
                    "user__profile_photo",
                    "user__subscription_type",
                )
                .annotate(total_points=Count("id"))
            )

            # --- Step 3: Ensure all friends (and self) are present, even with 0 points ---
            user_data_map = {u["user__id"]: u for u in leaderboard}
            all_users = User.objects.filter(id__in=friend_ids)

            results = []
            for index, u in enumerate(all_users, start=1):
                user_badge = UserBadge.objects.filter(user=u, is_completed=True).order_by('-id').first()
                total_points = user_data_map.get(u.id, {}).get("total_points", 0)

                results.append({
                    "user_id": u.id,
                    "first_name": u.first_name,
                    "profile_photo": request.build_absolute_uri(u.profile_photo.url) if getattr(u, 'profile_photo', None) else None,
                    "subscription_type": getattr(u, 'subscription_type', 'free'),
                    "total_points": total_points,
                    "level":total_points/20,
                    "rank": index,
                    "badge": {
                        "badge_id": user_badge.badge.id if user_badge else None,
                        "badge_name": user_badge.badge.name if user_badge else None,
                        "is_completed": user_badge.is_completed if user_badge else False,
                        "image": (
                        request.build_absolute_uri(user_badge.badge.image.url)
                        if (user_badge and user_badge.badge and user_badge.badge.image)
                        else None
                    )
                    }
                })

            # Sort by total points descending
            results = sorted(results, key=lambda x: x["total_points"], reverse=True)
            return results

        data = {
            "weekly": build_leaderboard(week_start),
            "monthly": build_leaderboard(month_start),
            "all_time": build_leaderboard(),
        }

        return Response(data)