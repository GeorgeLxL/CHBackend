from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from connecthearbackend.api.models import User


class UserLoginSerializer(TokenObtainPairSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    refresh = serializers.CharField(max_length=255, read_only=True)
    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
            data = {}
            refresh = self.get_token(user)
            data['refresh'] = str(refresh)
            data['token'] = str(refresh.access_token)
            data['access_token_expires_in'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            data['refresh_token_expires_in'] = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            data['email']= user.email
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return data



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name','email', 'password', 'academy', 'memberID')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user

class AdminLoginSerializer(TokenObtainPairSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    refresh = serializers.CharField(max_length=255, read_only=True)
    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        if not user.is_superuser:
            raise serializers.ValidationError(
                'A user with this email and password is not admin.'
            )
        try:
            data = {}
            refresh = self.get_token(user)
            data['refresh'] = str(refresh)
            data['token'] = str(refresh.access_token)
            data['access_token_expires_in'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            data['refresh_token_expires_in'] = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            data['email']= user.email
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return data
