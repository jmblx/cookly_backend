from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.recipe.common.service import RecipeService
from infrastructure.db.gateways.recipe_gateway import RecipeGateway


class DeleteRecipeHandler:
    def __init__(
        self,
        uow: Uow,
        recipe_service: RecipeService,
        idp: IdentityProvider,
        recipe_gateway: RecipeGateway,
    ):
        self.uow = uow
        self.recipe_service = recipe_service
        self.idp = idp
        self.recipe_gateway = recipe_gateway

    async def handle(self, recipe_id: int):
        user_id = await self.idp.get_current_user_id()
        recipe = await self.recipe_service.get_with_author_check(recipe_id, user_id)
        await self.recipe_gateway.delete(recipe)

        await self.uow.commit()
