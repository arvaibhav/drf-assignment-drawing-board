from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from endpoints.api.v1.serializers.user import UserLoginSerializer, UserSignupSerializer
from rest_framework import generics, status
from rest_framework.authtoken.models import Token


class UserSignupView(CreateAPIView):
    serializer_class = UserSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk}, status=status.HTTP_201_CREATED
        )


class UserLoginView(CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk})
