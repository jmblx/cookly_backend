from application.common.idp import IdentityProvider
from application.user.common.service import UserService
from infrastructure.db.models import Recipe


class GetUserFavoriteRecipesHandler:
    def __init__(self, user_service: UserService, idp: IdentityProvider):
        self.user_service = user_service
        self.idp = idp

    async def handle(
        self,
    ) -> list[Recipe]:
        user_id = await self.idp.get_current_user_id()
        return await self.user_service.get_favorite_recipes(
            user_id,
        )
