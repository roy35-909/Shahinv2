from rest_framework import serializers
from .models import Payment
from django.contrib.auth import get_user_model
User = get_user_model()

class SubscriptionSerializer(serializers.Serializer):
    subscription_type = serializers.ChoiceField(choices=User.SUBSCRIPTION_CHOICES)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'currency', 'status', 'stripe_payment_intent_id', 'created_at']
        read_only_fields = ['id', 'status', 'stripe_payment_intent_id', 'created_at']


