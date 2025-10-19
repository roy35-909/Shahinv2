from django.shortcuts import render

# Create your views here.
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer
from datetime import timedelta
from django.utils import timezone
stripe.api_key = settings.STRIPE_SECRET_KEY

# Price mapping
SUBSCRIPTION_PRICES = {
    'monthly': 4.99,
    'yearly': 39.99,
    'lifetime': 89.00
}

class SubscribeUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            subscription_type = serializer.validated_data['subscription_type']
            
            if subscription_type == 'free':
                request.user.subscription_type = 'free'
                request.user.subscription_start = None
                request.user.subscription_end = None
                request.user.save()
                return Response({"message": "Subscription set to Free"}, status=status.HTTP_200_OK)

            # Create Stripe PaymentIntent
            amount = int(SUBSCRIPTION_PRICES[subscription_type] * 100)  # in cents
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                customer=request.user.stripe_customer_id if request.user.stripe_customer_id else None,
                metadata={'user_id': request.user.id, 'subscription_type': subscription_type}
            )

            # Save pending payment
            Payment.objects.create(
                user=request.user,
                amount=SUBSCRIPTION_PRICES[subscription_type],
                currency='USD',
                status='pending',
                stripe_payment_intent_id=intent.id
            )

            return Response({
                "client_secret": intent.client_secret,
                "subscription_type": subscription_type
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StripeWebhookAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return Response(status=400)
        except stripe.error.SignatureVerificationError:
            return Response(status=400)

        # Handle payment success
        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            user_id = intent['metadata']['user_id']
            subscription_type = intent['metadata']['subscription_type']
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=intent['id'])
                payment.status = 'completed'
                payment.save()

                user = User.objects.get(id=user_id)
                user.subscription_type = subscription_type
                user.subscription_start = timezone.now()
                # set end date based on subscription type
                if subscription_type == 'monthly':
                    user.subscription_end = timezone.now() + timedelta(days=30)
                elif subscription_type == 'yearly':
                    user.subscription_end = timezone.now() + timedelta(days=365)
                elif subscription_type == 'lifetime':
                    user.subscription_end = None
                user.save()
            except Payment.DoesNotExist:
                pass

        return Response(status=200)
    

