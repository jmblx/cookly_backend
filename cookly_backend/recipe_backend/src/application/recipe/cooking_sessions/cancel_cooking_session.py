from application.common.interfaces.uow import Uow
from application.recipe.cooking_sessions.service import CookingService


class CancelCookingSessionHandler:
    def __init__(self, cooking_service: CookingService, uow: Uow):
        self.cooking_service = cooking_service
        self.uow = uow

    async def handle(self, session_id: int) -> None:
        await self.cooking_service.cancel_session(session_id)
        await self.uow.commit()
