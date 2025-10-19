from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to allow only admin (is_staff) users to get JWT tokens
    """
    def validate(self, attrs):
        # Standard validation to get tokens
        data = super().validate(attrs)

        # Check if user is admin
        if not self.user.is_superuser:
            raise serializers.ValidationError(
                {'detail': 'You do not have admin privileges.'}
            )

        # Add extra user info if needed
        data.update({
            'user_id': self.user.id,
            'email': self.user.email,
            'is_superuser': self.user.is_superuser
        })
        return data
    

class MonthlyRevenueSerializer(serializers.Serializer):
    month = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)