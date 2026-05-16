from datetime import timedelta
from uuid import UUID, uuid4

from application.common.auth_server_token_types import (
    AuthServerAccessToken,
    AuthServerRefreshTokenWithData,
)
from application.common.interfaces.auth_server_token_creation import (
    AuthServerTokenCreationService,
)
from application.common.interfaces.jwt_service import JWTService
from infrastructure.services.auth.config import JWTSettings


class AuthServerTokenCreationServiceImpl(AuthServerTokenCreationService):
    """Реализация сервиса создания токенов с использованием JWTService."""

    def __init__(self, jwt_settings: JWTSettings, jwt_service: JWTService):
        self.jwt_service = jwt_service
        self.jwt_settings = jwt_settings

    def create_auth_server_access_token(
        self, user_id: UUID, is_admin
    ) -> AuthServerAccessToken:
        jwt_payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "is_admin": is_admin,
        }
        encoded_token = self.jwt_service.encode(
            payload=jwt_payload,
            expire_minutes=self.jwt_settings.access_token_expire_minutes,
        )
        return AuthServerAccessToken(encoded_token["code"])

    async def create_auth_server_refresh_token(
        self, user_id: UUID, fingerprint: str
    ) -> AuthServerRefreshTokenWithData:
        jti = str(uuid4())
        jwt_payload = {"sub": str(user_id), "jti": jti}
        encoded_token = self.jwt_service.encode(
            payload=jwt_payload,
            expire_timedelta=timedelta(
                days=self.jwt_settings.refresh_token_expire_days
            ),
        )
        refresh_token_data = AuthServerRefreshTokenWithData(
            token=encoded_token["code"],
            user_id=user_id,
            jti=jti,
            fingerprint=fingerprint,
            created_at=encoded_token["created_at"],
        )
        return refresh_token_data
