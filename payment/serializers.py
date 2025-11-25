from rest_framework import serializers
from .models import Payment, SubscriptionPlan
from django.contrib.auth import get_user_model
User = get_user_model()

class SubscriptionSerializer(serializers.Serializer):
    subscription_type = serializers.ChoiceField(choices=User.SUBSCRIPTION_CHOICES)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'currency', 'status', 'stripe_payment_intent_id', 'created_at']
        read_only_fields = ['id', 'status', 'stripe_payment_intent_id', 'created_at']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'price']

class AppleSubscriptionSerializer(serializers.Serializer):
    receipt = serializers.CharField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(default="USD")
    
    SUBSCRIPTION_CHOICES = [
        ("free", "Free"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("lifetime", "Lifetime"),
    ]

    subscription_type = serializers.ChoiceField(
        choices=SUBSCRIPTION_CHOICES,
        default="free"
    )