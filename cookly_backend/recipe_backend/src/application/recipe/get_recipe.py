from application.common.idp import IdentityProvider
from infrastructure.db.gateways.recipe_gateway import RecipeGateway, RecipeWithRelations


class GetRecipeHandler:
    def __init__(self, recipe_gateway: RecipeGateway, idp: IdentityProvider):
        self.recipe_gateway = recipe_gateway
        self.idp = idp

    async def handle(self, recipe_id: int) -> RecipeWithRelations:
        return await self.recipe_gateway.get_with_relations(recipe_id, await self.idp.get_current_user_id())
