from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.user.common.service import UserService


class SetRecipeIsFavoriteHandler:
    def __init__(self, uow: Uow, user_service: UserService, idp: IdentityProvider):
        self.uow = uow
        self.user_service = user_service
        self.idp = idp

    async def handle(self, recipe_id: int, *, is_favorite: bool):
        user_id = await self.idp.get_current_user_id()
        user_recipe_record = await self.user_service.get_or_create_user_recipe_record(user_id, recipe_id)
        await self.user_service.set_recipe_favorite_value(
            user_recipe_record, value=is_favorite
        )
        await self.uow.commit()
