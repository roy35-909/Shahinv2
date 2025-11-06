from rest_framework import serializers
from django.db.models import QuerySet
from djoser.serializers import UserCreateSerializer
from .models import User,Badge,UserBadge, Device
class UserCreateSerializers(UserCreateSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id','email','first_name','password')

class NewUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["first_name", "email", "password"]



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=6)
    retype_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data["password"] != data["retype_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data


class UserTargetSerializer(serializers.ModelSerializer):
    target = serializers.ListField(
        child=serializers.ChoiceField(choices=User.CATEGORY_CHOICES),
        allow_empty=False
    )

    class Meta:
        model = User
        fields = ['target']

    def update(self, instance, validated_data):
        instance.target = validated_data.get('target', instance.target)
        instance.save()
        return instance
    

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer()
    class Meta:
        model = UserBadge
        fields = '__all__'


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device

        fields = ['token', 'platform']


class AppleLoginSerializer(serializers.Serializer):
    identity_token = serializers.CharField(required=True, help_text="Apple identity token (JWT)")
    full_name = serializers.CharField(required=False, allow_blank=True)

class GoogleLoginSerializer(serializers.Serializer):
    idToken = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    provider = serializers.CharField(required=False)
    