from datetime import datetime
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.errors.exceptions import PermissionDeniedError
from application.common.idp import IdentityProvider
from application.recipe.common.exceptions import SessionIsNotActiveError
from application.user.common.preference_service import PreferenceProfileService
from domain.entities.value_objects import CookingSessionStatus
from infrastructure.db.gateways.cooking_session_gateway import CookingSessionGateway
from infrastructure.db.models import CookingSession, Recipe, RecipeStep


class CookingService:
    def __init__(
        self,
        session: AsyncSession,
        gateway: CookingSessionGateway,
        tz: ZoneInfo,
        idp: IdentityProvider,
        preference_profile_service: PreferenceProfileService,
    ) -> None:
        self.session = session
        self.gateway = gateway
        self.tz = tz
        self.idp = idp
        self.preference_profile_service = preference_profile_service

    async def start_session(self, user_id: UUID, recipe_id: int) -> int:
        cooking_session = await self.gateway.get_active_cooking_session(user_id, recipe_id)
        if not cooking_session:
            cooking_session = CookingSession(user_id=user_id, recipe_id=recipe_id)
        await self.gateway.save(cooking_session)
        return cooking_session.id

    async def _get_session(self, session_id: int, *, only_active: bool = False) -> CookingSession:
        cooking_session = await self.gateway.get_by_id(session_id)
        if cooking_session.user_id != await self.idp.get_current_user_id():
            raise PermissionDeniedError("you are not the owner of this session")
        if only_active and cooking_session.status != CookingSessionStatus.active.value:
            raise SessionIsNotActiveError
        return cooking_session

    async def change_session_active_step(self, session_id: int, step_numer: int) -> None:
        cooking_session = await self._get_session(session_id)
        cooking_session.current_step = step_numer
        await self.gateway.save(cooking_session)

    async def cancel_session(self, session_id: int) -> None:
        cooking_session = await self._get_session(session_id, only_active=True)
        cooking_session.status = CookingSessionStatus.cancelled.value
        cooking_session.end_time = datetime.now(self.tz)
        await self.gateway.save(cooking_session)

    async def finish_session(self, session_id: int) -> None:
        cooking_session = await self._get_session(session_id, only_active=True)
        cooking_session.status = CookingSessionStatus.finished.value
        cooking_session.end_time = datetime.now(self.tz)
        await self.gateway.save(cooking_session)
        await self.preference_profile_service.recalculate(cooking_session.user_id)

    async def get_user_active_sessions(self) -> list[dict[str, Any]]:
        stmt = (
            select(
                CookingSession,
                Recipe.id.label("recipe_id"),
                Recipe.title.label("recipe_title"),
                RecipeStep.title.label("step_title"),
            )
            .join(Recipe, CookingSession.recipe_id == Recipe.id)
            .join(
                RecipeStep,
                and_(
                    RecipeStep.recipe_id == CookingSession.recipe_id,
                    RecipeStep.number == CookingSession.current_step
                )
            )
            .where(
                CookingSession.user_id == await self.idp.get_current_user_id(),
                CookingSession.status == CookingSessionStatus.active.value
            )
        )
        result = await self.session.execute(stmt)

        rows = result.all()

        return [
            {
                "session": row[0],
                "recipe_id": row[1],
                "recipe_title": row[2],
                "step_title": row[3],
            }
            for row in rows
        ]
