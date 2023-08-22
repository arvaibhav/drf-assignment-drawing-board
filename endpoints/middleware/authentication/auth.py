import datetime
from jwt import ExpiredSignatureError, InvalidTokenError, encode, decode
from rest_framework.permissions import BasePermission

from config_manager import get_config

jwt_config = get_config().JWT_CONFIG


class TokenPayload:
    def payload(self):
        return {k: getattr(self, k) for k in vars(self)}


class UserAccessTokenPayload(TokenPayload):
    def __init__(self, user_id):
        self.user_id = user_id


class UserRefreshTokenPayload(TokenPayload):
    def __init__(self, token_id):
        self.token_id = token_id


def create_access_token(token_payload: TokenPayload):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=jwt_config.EXPIRE_IN_SEC
    )
    return encode(
        {**token_payload.payload(), "exp": exp_time},
        jwt_config.SECRET_KEY,
        algorithm="HS256",
    )


def create_refresh_token(token_payload: TokenPayload):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=jwt_config.REFRESH_EXPIRE_IN_SEC
    )
    return encode(
        {**token_payload.payload(), "exp": exp_time},
        jwt_config.REFRESH_SECRET_KEY,
        algorithm="HS256",
    )


def validate_token(token, secret_key, algorithm="HS256"):
    try:
        payload = decode(token, secret_key, algorithms=[algorithm])
        return payload
    except ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except Exception as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")


def validate_access_token(token) -> dict:
    """
    Validates the access token.

    :param token: The token to validate.
    :return: A dictionary with the token data.
    :raises: Any exception that might be raised by the validate_token function.
    """
    return validate_token(token, secret_key=jwt_config.SECRET_KEY, algorithm="HS256")


def validate_refresh_token(token) -> dict:
    """
    Validates the access token.

    :param token: The token to validate.
    :return: A dictionary with the token data.
    :raises: Any exception that might be raised by the validate_token function.
    """
    return validate_token(
        token, secret_key=jwt_config.REFRESH_SECRET_KEY, algorithm="HS256"
    )


class JwtAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        user_id = getattr(request, "user_id", None)

        return True
