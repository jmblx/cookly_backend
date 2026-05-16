from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models import CookingSession


class CookingSessionGateway:
    def __init__(self, session: AsyncSession, tz: ZoneInfo):
        self.session = session
        self.tz = tz

    async def save(self, cooking_session: CookingSession) -> None:
        cooking_session.last_activity = datetime.now(self.tz)
        self.session.add(cooking_session)
        await self.session.flush()

    async def get_by_id(self, cooking_session_id: int) -> CookingSession | None:
        return await self.session.get(CookingSession, cooking_session_id)

    async def get_active_cooking_session(self, user_id: UUID, recipe_id: int) -> CookingSession | None:
        existing_session_query = select(CookingSession).where(
            CookingSession.user_id == user_id,
            CookingSession.recipe_id == recipe_id,
            CookingSession.end_time is None
        )
        return (await self.session.execute(existing_session_query)).scalar_one_or_none()
