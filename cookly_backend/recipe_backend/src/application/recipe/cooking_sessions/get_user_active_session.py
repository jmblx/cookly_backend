from typing import Any

from application.common.interfaces.uow import Uow
from application.recipe.cooking_sessions.service import CookingService


class GetUserCookingSessionHandler:
    def __init__(self, cooking_service: CookingService, uow: Uow):
        self.cooking_service = cooking_service
        self.uow = uow

    async def handle(self) -> list[dict[str, Any]]:
        user_active_cooking_sessions = await self.cooking_service.get_user_active_sessions()
        await self.uow.commit()
        return user_active_cooking_sessions
