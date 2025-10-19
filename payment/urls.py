from django.urls import include, path
from .views import *

urlpatterns = [
    path('subscribe/', SubscribeUserAPIView.as_view(), name='subscribe'),
    path('stripe-webhook/', StripeWebhookAPIView.as_view(), name='stripe-webhook'),
]