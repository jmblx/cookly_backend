from datetime import timedelta
from uuid import UUID, uuid4

from redis.asyncio import Redis

from application.user.reset_pwd.service import (
    ResetPasswordCode,
    ResetPasswordToken,
    ResetPwdService,
)


class ResetPwdServiceImpl(ResetPwdService):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_password_reset_code(
        self, user_id: UUID, code: ResetPasswordCode
    ) -> None:
        await self.redis.set(
            f"reset_password_code:{code}",
            str(user_id),
            ex=timedelta(minutes=15),
        )

    async def get_user_id_from_reset_pwd_code(
        self, code: ResetPasswordCode
    ) -> UUID | None:
        user_id = await self.redis.get(f"reset_password_code:{code}")
        return UUID(user_id) if user_id else None

    async def delete_reset_pwd_code(self, code: ResetPasswordCode) -> None:
        await self.redis.delete(f"reset_password_code:{code}")

    async def generate_reset_token(self, user_id: UUID) -> ResetPasswordToken:
        token = str(uuid4())
        await self.redis.set(
            f"reset_password_token:{token}",
            str(user_id),
            ex=timedelta(minutes=10),
        )
        return ResetPasswordToken(token)

    async def get_user_id_from_reset_token(
        self, token: ResetPasswordToken
    ) -> UUID | None:
        user_id = await self.redis.get(f"reset_password_token:{token}")
        return UUID(user_id) if user_id else None

    async def delete_reset_token(self, token: ResetPasswordToken) -> None:
        await self.redis.delete(f"reset_password_token:{token}")
