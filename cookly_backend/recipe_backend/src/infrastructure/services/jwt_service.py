import jwt

from application.common.errors.base import InvalidTokenError, TokenExpiredError
from application.common.types import AccessToken, AccessTokenPayload
from core.config import JWTConfig


class JWTService:
    """Реализация сервиса работы с JWT токенами."""
    def __init__(self, jwt_config: JWTConfig):
        self.jwt_config = jwt_config

    def decode(
        self, token: AccessToken
    ) -> AccessTokenPayload:
        """Декодирует JWT токен и возвращает его payload."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_config.public_key,
                algorithms=[self.jwt_config.algorithm],
            )
        except jwt.ExpiredSignatureError as err:
            raise TokenExpiredError from err
        except jwt.DecodeError as err:
            raise InvalidTokenError from err
        else:
            return payload
