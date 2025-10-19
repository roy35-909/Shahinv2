from django.urls import path
from . import views

urlpatterns = [
    path('send_friend_request/', views.SendFriendRequestAPIView.as_view(), name='send_friend_request'),
    path('accept_friend_request/', views.AcceptFriendRequestAPIView.as_view(), name='accept_friend_request'),
    path('list_friend_requests/', views.ListFriendRequestsAPIView.as_view(), name='list_friend_requests'),
    path('cancel_friend_request/', views.CancelFriendRequestAPIView.as_view(), name='cancel_friend_request'),
    path('list_friends/', views.ListFriendsAPIView.as_view(), name='list_friends'),
    path('friends/search/', views.SearchUserAPIView.as_view(), name='search_user'),
    
    path('leaderboard/global/', views.LeaderboardAPIView.as_view(), name='Global LeaderBoard'),
    path('leaderboard/friends/', views.FriendLeaderboardAPIView.as_view(), name='Friends LeaderBoard'),

]