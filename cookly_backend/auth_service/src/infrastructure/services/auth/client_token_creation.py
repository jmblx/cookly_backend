import logging
from datetime import timedelta
from uuid import UUID, uuid4

from application.common.client_token_types import (
    ClientAccessToken,
    ClientRefreshTokenWithData,
)
from application.common.interfaces.client_token_creation import (
    ClientTokenCreationService,
)
from application.common.interfaces.jwt_service import JWTService
from infrastructure.services.auth.config import JWTSettings

logger = logging.getLogger(__name__)


class ClientTokenCreationServiceImpl(ClientTokenCreationService):
    def __init__(self, jwt_settings: JWTSettings, jwt_service: JWTService):
        self.jwt_service = jwt_service
        self.jwt_settings = jwt_settings

    def create_client_access_token(
        self, user_id: UUID, user_scopes: list[str], client_id: int, rs_ids: list[int]
    ) -> ClientAccessToken:
        logger.info("scopes: %s", user_scopes)
        jwt_payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "scopes": user_scopes,
            "client_id": client_id,
            "rs_ids": rs_ids,
        }
        encoded_token = self.jwt_service.encode(
            payload=jwt_payload,
            expire_minutes=self.jwt_settings.access_token_expire_minutes,
        )
        return ClientAccessToken(encoded_token["code"])

    async def create_client_refresh_token(
        self, user_id: UUID, client_id, rs_ids
    ) -> ClientRefreshTokenWithData:
        jti = str(uuid4())
        jwt_payload = {
            "sub": str(user_id),
            "jti": jti,
            "client_id": client_id,
            "rs_ids": rs_ids,
        }
        encoded_token = self.jwt_service.encode(
            payload=jwt_payload,
            expire_timedelta=timedelta(
                days=self.jwt_settings.refresh_token_expire_days
            ),
        )
        refresh_token_data = ClientRefreshTokenWithData(
            token=encoded_token["code"],  # type: ignore
            user_id=user_id,
            jti=jti,
            created_at=encoded_token["created_at"],
        )
        return refresh_token_data
