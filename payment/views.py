from django.shortcuts import render


import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User, SubscriptionPlan,Payment
from .serializers import SubscriptionSerializer, PaymentSerializer, SubscriptionPlanSerializer
from datetime import timedelta
from django.utils import timezone
from .tasks import expire_subscription
stripe.api_key = settings.STRIPE_SECRET_KEY




# class SubscribeUserAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         serializer = SubscriptionSerializer(data=request.data)
#         try:
#             monthly_price = SubscriptionPlan.objects.get(name='monthly')
#         except:
#             monthly_price = 4.99

#         try:
#             yearly_price = SubscriptionPlan.objects.get(name='yearly')
#         except:
#             yearly_price = 39.99

#         try:
#             lifetime_price = SubscriptionPlan.objects.get(name='lifetime')
#         except:
#             lifetime_price = 89.00

#         SUBSCRIPTION_PRICES = {
#             'monthly': monthly_price,
#             'yearly': yearly_price,
#             'lifetime': lifetime_price
#         }
#         if serializer.is_valid():
#             subscription_type = serializer.validated_data['subscription_type']
            
#             if subscription_type == 'free':
#                 request.user.subscription_type = 'free'
#                 request.user.subscription_start = None
#                 request.user.subscription_end = None
#                 request.user.save()
#                 return Response({"message": "Subscription set to Free"}, status=status.HTTP_200_OK)

#             # Create Stripe PaymentIntent
#             amount = int(SUBSCRIPTION_PRICES[subscription_type] * 100)  # in cents
#             intent = stripe.PaymentIntent.create(
#                 amount=amount,
#                 currency='usd',
#                 customer=request.user.stripe_customer_id if request.user.stripe_customer_id else None,
#                 metadata={'user_id': request.user.id, 'subscription_type': subscription_type}
#             )

#             # Save pending payment
#             Payment.objects.create(
#                 user=request.user,
#                 amount=SUBSCRIPTION_PRICES[subscription_type],
#                 currency='USD',
#                 status='pending',
#                 stripe_payment_intent_id=intent.id
#             )

#             return Response({
#                 "client_secret": intent.client_secret,
#                 "subscription_type": subscription_type
#             }, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SubscribeUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subscription_type = serializer.validated_data['subscription_type']

        def get_price(plan_name, default):
            try:
                return SubscriptionPlan.objects.get(name=plan_name).price
            except:
                return default

        SUBSCRIPTION_PRICES = {
            'monthly': get_price('monthly', 4.99),
            'yearly': get_price('yearly', 39.99),
            'lifetime': get_price('lifetime', 89.00),
        }

        if subscription_type == 'free':
            request.user.subscription_type = 'free'
            request.user.subscription_start = None
            request.user.subscription_end = None
            request.user.save()
            return Response({"message": "Subscription set to Free"}, status=status.HTTP_200_OK)

        amount = int(SUBSCRIPTION_PRICES[subscription_type] * 100)

        # 👇 Use your backend domain here
        backend_domain = request.build_absolute_uri('/')[:-1]
        print(backend_domain)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{subscription_type.capitalize()} Subscription',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id,
                'subscription_type': subscription_type
            },
            success_url=f'{backend_domain}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{backend_domain}/payment/cancel?session_id={{CHECKOUT_SESSION_ID}}'
        )

        Payment.objects.create(
            user=request.user,
            amount=SUBSCRIPTION_PRICES[subscription_type],
            currency='USD',
            status='pending',
            stripe_payment_intent_id=session.payment_intent,
            stripe_session_id=session.id,
        )

        return Response({
            "checkout_url": session.url,
            "subscription_type": subscription_type
        }, status=status.HTTP_200_OK)


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
    

class StripeSuccessAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"error": "Session ID missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            intent = stripe.PaymentIntent.retrieve(session.payment_intent)

            user_id = session.metadata.get("user_id")
            subscription_type = session.metadata.get("subscription_type")

            payment = Payment.objects.get(stripe_session_id=session_id)
            payment.status = 'completed'
            payment.save()

            user = User.objects.get(id=user_id)
            user.subscription_type = subscription_type
            user.subscription_start = timezone.now()

            if subscription_type == 'monthly':
                user.subscription_end = timezone.now() + timedelta(days=30)
            elif subscription_type == 'yearly':
                user.subscription_end = timezone.now() + timedelta(days=365)
            elif subscription_type == 'lifetime':
                user.subscription_end = None

            user.save()
            if user.subscription_end:
                expire_subscription.apply_async(
                    args=[user.id],
                    eta=user.subscription_end
                )
            return Response({
                "message": "Payment successful",
                "subscription_type": subscription_type,
                "amount": payment.amount,
                "status": "completed"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeCancelAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(stripe_session_id=session_id)
        payment.delete()
        
        return Response({
            "message": "Payment canceled or not completed",
            "status": "canceled"
        }, status=status.HTTP_200_OK)
    


class SubscriptionPlansAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):

        plans = SubscriptionPlan.objects.exclude(name__iexact="free")
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)