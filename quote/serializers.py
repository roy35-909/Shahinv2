
from rest_framework import serializers
from .models import UserSchedule

class UserScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSchedule
        fields = ['start_time', 'end_time', 'interval_minutes']

    def validate_start_time(self, value):
        # Add custom validation for start_time if needed
        return value

    def validate_end_time(self, value):
        # Add custom validation for end_time if needed
        return value

    def validate_interval_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Interval must be a positive integer.")
        return value