import uuid

from redis.asyncio import Redis

from application.common.interfaces.http_auth import SessionID


class HttpAdminSessionService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create_and_save_session(
        self,
        admin_username: str,
    ) -> SessionID:
        session_id = SessionID(uuid.uuid4())
        await self.redis.set(
            f"admin:session:{admin_username}", str(session_id)
        )
        return session_id
