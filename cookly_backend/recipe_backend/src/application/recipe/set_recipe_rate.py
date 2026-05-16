from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.recipe.common.exceptions import AuthorRecipeRateError, InvalidRecipeRateError
from application.recipe.common.value_objects import MAX_RECIPE_RATE, MIN_RECIPE_RATE
from application.user.common.service import UserService


class AddRecipeRateHandler:
    def __init__(self, uow: Uow, user_service: UserService, idp: IdentityProvider):
        self.uow = uow
        self.user_service = user_service
        self.idp = idp

    async def handle(self, recipe_id: int, rate: int):
        user_id = await self.idp.get_current_user_id()
        user_recipe_record = await self.user_service.get_or_create_user_recipe_record(user_id, recipe_id)
        if await self.user_service.check_is_author_recipe(user_id, recipe_id):
            raise AuthorRecipeRateError
        if rate > MAX_RECIPE_RATE or rate < MIN_RECIPE_RATE:
            raise InvalidRecipeRateError
        await self.user_service.set_user_recipe_rate(
            user_recipe_record,
            rate,
        )
        await self.uow.commit()
