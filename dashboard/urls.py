
from django.urls import path
from .views import (
    AdminTokenObtainPairView,
    RevenueReportAPIView,
    DashboardAPIView,
    WeeklyUserQuoteActivityAPIView,
    SubscriptionDistributionAPIView,

)

urlpatterns = [
    path('login/', AdminTokenObtainPairView.as_view(), name='admin-login'),
    path('revenue_report/', RevenueReportAPIView.as_view(), name='Revenue Report'),
    path('dashboard_data/', DashboardAPIView.as_view(), name='Dashboard Data'),
    path('weekly_user_activity/', WeeklyUserQuoteActivityAPIView.as_view(), name='Dashboard Data'),
    path('subscription_distribution/', SubscriptionDistributionAPIView.as_view(), name='Subscription Distribution'),
]