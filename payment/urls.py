from django.urls import include, path
from .views import *

urlpatterns = [
    path('subscribe/', SubscribeUserAPIView.as_view(), name='subscribe'),
    # path('stripe-webhook/', StripeWebhookAPIView.as_view(), name='stripe-webhook'),
    path('success/', StripeSuccessAPIView.as_view(), name='success'),
    path('cancel/', StripeCancelAPIView.as_view(), name='cancel'),
    path('plans/', SubscriptionPlansAPIView.as_view(), name='subscription-plans'),
    path('apple/subscribe/', AppleReceiptVerifyAPIView.as_view(), name='apple-subscribe'),
]