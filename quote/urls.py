from django.urls import include, path

from .views import (
    ListUserQuoteHistory,
    LikedUserQuote,
    SavedUserQuote,
    ShareUserQuote,
    GetSavedUserQuote,
    GetLikedUserQuote,
    UserScheduleAPIView,
    QuoteListAPIView,
    ViewedUserQuote
)
urlpatterns = [

    path('create_schedule', UserScheduleAPIView.as_view(), name="User Schedule API View"),
    path('quote/history/', ListUserQuoteHistory.as_view(), name='quote-history'),
    path('quote/scroll_list/', QuoteListAPIView.as_view(), name='quote-scroll-list'),
    path('quote/like/<int:pk>/', LikedUserQuote.as_view(), name='like-quote'),
    path('quote/save/<int:pk>/', SavedUserQuote.as_view(), name='save-quote'),
    path('quote/viewed/<int:pk>/', ViewedUserQuote.as_view(), name='liked-quotes'),
    path('quote/share/<int:pk>/', ShareUserQuote.as_view(), name='share-quote'),
    path('quote/saved/', GetSavedUserQuote.as_view(), name='saved-quotes'),
    path('quote/liked/', GetLikedUserQuote.as_view(), name='liked-quotes'),
    
]