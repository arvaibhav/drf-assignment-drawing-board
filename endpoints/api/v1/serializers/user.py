from django.contrib.auth import authenticate
from rest_framework import serializers
from db.models import User
from endpoints.middleware.authentication.auth import validate_access_token
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid username or password")
        return {"user": user}


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")

        # Here you'll call your method to validate the access token
        payload = validate_access_token(refresh_token)

        token_id = payload.get("token_id")
        user_id = payload.get("user_id")

        # Check if the user and token ID combination exists
        if not Token.objects.filter(user_id=user_id, key=token_id).exists():
            raise ValidationError("Invalid or expired token.")

        return attrs
