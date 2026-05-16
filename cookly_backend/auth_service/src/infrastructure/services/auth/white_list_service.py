import logging
from uuid import UUID

from redis.asyncio import Redis

from application.common.auth_server_token_types import (
    AuthServerRefreshTokenData,
    AuthServerRefreshTokenWithData,
)
from application.common.client_token_types import (
    ClientRefreshTokenData,
    ClientRefreshTokenWithData,
)
from application.common.interfaces.white_list import (
    AuthServerTokenWhitelistService,
    ClientTokenWhitelistService,
)

logger = logging.getLogger(__name__)


class AuthServerTokenWhitelistServiceImpl(AuthServerTokenWhitelistService):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.audience = "auth_server"

    def _serialize_refresh_token_data(
        self, refresh_token_data: AuthServerRefreshTokenWithData
    ) -> dict[str, str]:
        return {
            "jti": str(refresh_token_data.jti),
            "user_id": str(refresh_token_data.user_id),
            "fingerprint": refresh_token_data.fingerprint,
            "created_at": refresh_token_data.created_at.isoformat(),
        }

    async def _remove_token_by_jti(self, jti: UUID) -> None:
        token_data = await self.get_refresh_token_data(jti)
        if not token_data:
            return
        await self.redis.delete(f"{self.audience}_refresh_token:{jti}")
        await self.redis.zrem(
            f"{self.audience}_refresh_tokens:{token_data.user_id}", jti
        )

    async def is_fingerprint_matching(
        self, jti: UUID, fingerprint: str
    ) -> bool:
        token_data = await self.redis.hgetall(
            f"{self.audience}_refresh_token:{jti}"
        )
        return (
            token_data.get("fingerprint") == fingerprint
            if token_data
            else False
        )

    async def replace_refresh_token(
        self, refresh_token_data: AuthServerRefreshTokenWithData, limit: int
    ) -> None:
        print(f"Replace refresh token with data: {refresh_token_data}")
        user_id = refresh_token_data.user_id
        jti = refresh_token_data.jti
        created_at = refresh_token_data.created_at.timestamp()

        if (
            await self.redis.zcard(f"{self.audience}_refresh_tokens:{user_id}")
            >= limit
        ):
            oldest = await self.redis.zrange(
                f"{self.audience}_refresh_tokens:{user_id}", 0, 0
            )
            if oldest:
                await self._remove_token_by_jti(oldest[0])

        await self.redis.hset(
            f"{self.audience}_refresh_token:{jti}",
            mapping=self._serialize_refresh_token_data(refresh_token_data),
        )
        await self.redis.zadd(
            f"{self.audience}_refresh_tokens:{user_id}", {jti: created_at}
        )

    async def get_refresh_token_data(
        self, jti: UUID
    ) -> AuthServerRefreshTokenData | None:
        data = await self.redis.hgetall(f"{self.audience}_refresh_token:{jti}")
        return (
            AuthServerRefreshTokenData(**data)
            if data and isinstance(data, dict)
            else None
        )

    async def remove_old_tokens(
        self, user_id: UUID, fingerprint: str, limit: int
    ) -> None:
        if (
            await self.redis.zcard(f"{self.audience}_refresh_tokens:{user_id}")
            > limit
        ):
            oldest = await self.redis.zrange(
                f"{self.audience}_refresh_tokens:{user_id}", 0, 0
            )
            if oldest:
                await self._remove_token_by_jti(oldest[0])

    async def remove_token(self, jti: UUID) -> None:
        await self._remove_token_by_jti(jti)

    async def remove_tokens_except_current(
        self, jti: UUID, user_id: UUID
    ) -> None:
        tokens = await self.redis.zrange(
            f"{self.audience}_refresh_tokens:{user_id}", 0, -1
        )
        to_remove = [t for t in tokens if t != str(jti)]
        for token in to_remove:
            await self._remove_token_by_jti(token)
        if to_remove:
            await self.redis.zrem(
                f"{self.audience}_refresh_tokens:{user_id}", *to_remove
            )


class ClientTokenWhitelistServiceImpl(ClientTokenWhitelistService):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.audience = "client"

    def _serialize_refresh_token_data(
        self, refresh_token_data: ClientRefreshTokenData
    ) -> dict[str, str]:
        return {
            "jti": str(refresh_token_data.jti),
            "user_id": str(refresh_token_data.user_id),
            "created_at": refresh_token_data.created_at.isoformat(),
        }

    async def _remove_token_by_jti(self, jti: UUID) -> None:
        token_data = await self.get_refresh_token_data(jti)
        if not token_data:
            return
        await self.redis.delete(f"{self.audience}_refresh_token:{jti}")
        await self.redis.zrem(
            f"{self.audience}_refresh_tokens:{token_data.user_id}", jti
        )

    async def replace_refresh_token(
        self, refresh_token_data: ClientRefreshTokenWithData, limit: int
    ) -> None:
        user_id = refresh_token_data.user_id
        jti = refresh_token_data.jti
        created_at = refresh_token_data.created_at.timestamp()

        if (
            await self.redis.zcard(f"{self.audience}_refresh_tokens:{user_id}")
            >= limit
        ):
            oldest = await self.redis.zrange(
                f"{self.audience}_refresh_tokens:{user_id}", 0, 0
            )
            if oldest:
                await self._remove_token_by_jti(oldest[0])

        await self.redis.hset(
            f"{self.audience}_refresh_token:{jti}",
            mapping=self._serialize_refresh_token_data(refresh_token_data),
        )
        await self.redis.zadd(
            f"{self.audience}_refresh_tokens:{user_id}", {jti: created_at}
        )

    async def get_refresh_token_data(
        self, jti: UUID
    ) -> ClientRefreshTokenData | None:
        data = await self.redis.hgetall(f"{self.audience}_refresh_token:{jti}")
        return ClientRefreshTokenData(**data) if data else None

    async def remove_old_tokens(self, user_id: UUID, limit: int) -> None:
        if (
            await self.redis.zcard(f"{self.audience}_refresh_tokens:{user_id}")
            > limit
        ):
            oldest = await self.redis.zrange(
                f"{self.audience}_refresh_tokens:{user_id}", 0, 0
            )
            if oldest:
                await self._remove_token_by_jti(oldest[0])

    async def remove_token(self, jti: UUID) -> None:
        await self._remove_token_by_jti(jti)

    async def remove_tokens_except_current(
        self, jti: UUID, user_id: UUID
    ) -> None:
        tokens = await self.redis.zrange(
            f"{self.audience}_refresh_tokens:{user_id}", 0, -1
        )
        to_remove = [t for t in tokens if t != str(jti)]
        for token in to_remove:
            await self._remove_token_by_jti(token)
        if to_remove:
            await self.redis.zrem(
                f"{self.audience}_refresh_tokens:{user_id}", *to_remove
            )
