import logging

import orjson
import redis.asyncio as aioredis

from application.common.services.auth_code import (
    AuthCodeDataInput,
    AuthorizationCodeStorage, AuthCodeData,
)

logger = logging.getLogger(__name__)


class RedisAuthorizationCodeStorage(AuthorizationCodeStorage):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    async def store_auth_code_data(
        self, auth_code: str, data: AuthCodeDataInput, expiration_time: int = 600
    ) -> None:
        ref = data["ref"]
        if ref.resource_servers:
            await self.redis_client.sadd(
                f"auth_code:{auth_code}:rs_ids", *[rs.id for rs in ref.resource_servers]
            )
            await self.redis_client.expire(
                f"auth_code:{auth_code}:rs_ids", expiration_time
            )

        json_data = orjson.dumps(
            {"user_data_needed": ref.user_scopes.value}
        )
        await self.redis_client.set(
            f"auth_code:{auth_code}:user_data_needed",
            json_data,
            ex=expiration_time,
        )

        json_data = orjson.dumps(data | {"client_id": ref.client_id})
        await self.redis_client.set(
            f"auth_code:{auth_code}", json_data, ex=expiration_time
        )

    async def retrieve_auth_code_data(
        self, auth_code: str
    ) -> AuthCodeData | None:
        raw_data = await self.redis_client.get(f"auth_code:{auth_code}")
        if not raw_data:
            return None

        data_dict = orjson.loads(raw_data)
        rs_ids = await self.redis_client.smembers(
            f"auth_code:{auth_code}:rs_ids"
        )
        data_dict["rs_ids"] = list(map(int, rs_ids)) if rs_ids else []

        user_data_needed_raw = await self.redis_client.get(
            f"auth_code:{auth_code}:user_data_needed"
        )
        if user_data_needed_raw:
            data_dict["user_data_needed"] = orjson.loads(user_data_needed_raw)[
                "user_data_needed"
            ]
        else:
            data_dict["user_data_needed"] = []
        logger.info(f"Retrieved auth code data: {data_dict}")
        return AuthCodeData(**data_dict)

    async def delete_auth_code_data(self, auth_code: str) -> None:
        await self.redis_client.delete(f"auth_code:{auth_code}")
