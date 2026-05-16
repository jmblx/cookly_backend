from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.recipe.cooking_sessions.service import CookingService


class StartCookingSessionHandler:
    def __init__(self, idp: IdentityProvider, cooking_service: CookingService, uow: Uow):
        self.idp = idp
        self.cooking_service = cooking_service
        self.uow = uow

    async def handle(self, recipe_id: int) -> int:
        user_id = await self.idp.get_current_user_id()
        cooking_session_id = await self.cooking_service.start_session(user_id, recipe_id)
        await self.uow.commit()
        return cooking_session_id
