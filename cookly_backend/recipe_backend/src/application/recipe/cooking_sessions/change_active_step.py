from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.recipe.cooking_sessions.service import CookingService


class ChangeStepCookingSessionHandler:
    def __init__(self, idp: IdentityProvider, cooking_service: CookingService, uow: Uow):
        self.idp = idp
        self.cooking_service = cooking_service
        self.uow = uow

    async def handle(self, session_id: int, new_active_step_number: int) -> None:
        await self.cooking_service.change_session_active_step(session_id, new_active_step_number)
        await self.uow.commit()
