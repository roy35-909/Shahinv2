from authentication.models import Friendship
from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from shahin.base import NewAPIView
from django.db.models import Q
from rest_framework.views import APIView
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

        
        friendship, created = Friendship.objects.get_or_create(user1=user1, user2=user2)
        
        if not created:
            if friendship.status != Friendship.PENDING:
                return Response({'detail': 'Friend request already sent or accepted/rejected.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Friend request is already pending.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        friendship.send_request()
        return Response(FriendshipSerializer(friendship).data, status=status.HTTP_201_CREATED)


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
        return Response(FriendshipSerializer(friendship).data, status=status.HTTP_200_OK)


class ListFriendRequestsAPIView(NewAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendshipSerializer
    def get(self, request, *args, **kwargs):
        user = request.user
        # Get all pending requests for this user (requests they are receiving)
        pending_requests = Friendship.objects.filter(user2=user, status=Friendship.PENDING)
        serializer = FriendshipSerializer(pending_requests, many=True)
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
        return Response({'detail': 'Friend request canceled.'}, status=status.HTTP_204_NO_CONTENT)


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

        # Perform a case-insensitive search on both the username (name) and email fields
        users = User.objects.filter(
            Q(username__icontains=search_term) |
            Q(email__icontains=search_term)
        )

        if users.exists():
            serializer = UserSearchSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No users found matching the search criteria.'}, status=status.HTTP_404_NOT_FOUND)