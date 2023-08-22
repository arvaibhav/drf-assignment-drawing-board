from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from endpoints.api.v1.serializers.user import (
    UserLoginSerializer,
    UserSignupSerializer,
    RefreshTokenSerializer,
)
from rest_framework import status
from rest_framework.authtoken.models import Token

from endpoints.middleware.authentication.auth import (
    jwt_config,
    validate_access_token,
    create_access_token,
    create_refresh_token,
    UserAccessTokenPayload,
    UserRefreshTokenPayload,
)


def generate_user_token(user_id):
    token, _ = Token.objects.get_or_create(user_id=user_id)
    access_token = create_access_token(
        token_payload=UserAccessTokenPayload(user_id=user_id)
    )
    refresh_token = create_refresh_token(
        token_payload=UserRefreshTokenPayload(token_id=token.pk)
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_ttl": jwt_config.EXPIRE_IN_SEC,
        "refresh_token_ttl": jwt_config.REFRESH_EXPIRE_IN_SEC,
    }


class UserSignupView(CreateAPIView):
    serializer_class = UserSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_response = generate_user_token(user.pk)
        return Response(token_response, status=status.HTTP_201_CREATED)


class UserLoginView(CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token_response = generate_user_token(user.pk)
        return Response(token_response, status=status.HTTP_201_CREATED)


class RefreshTokenView(CreateAPIView):
    serializer_class = RefreshTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = validate_access_token(request.data.get("refresh_token"))
        user_id = payload.get("user_id")

        access_token = create_access_token(
            token_payload=UserAccessTokenPayload(user_id=user_id)
        )
        return Response({"access_token": access_token}, status=status.HTTP_200_OK)
