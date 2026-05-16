import typing

from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from infrastructure.db.models import RecipeCategory


class GetAllRecipeCategoriesHandler:
    def __init__(self, recipe_gateway: RecipeGateway):
        self.recipe_gateway = recipe_gateway

    async def handle(self) -> list[RecipeCategory]:
        return typing.cast(list, await self.recipe_gateway.get_all_recipe_categories())
