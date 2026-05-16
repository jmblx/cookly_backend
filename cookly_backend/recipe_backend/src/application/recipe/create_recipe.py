from zoneinfo import ZoneInfo

from application.common.interfaces.uow import Uow
from application.recipe.common.service import RecipeService
from presentation.web_api.routes.recipe.schemas import RecipeFullRequest


class CreateRecipeHandler:
    def __init__(self, uow: Uow, recipe_service: RecipeService, tz: ZoneInfo):
        self.uow = uow
        self.recipe_service = recipe_service
        self.tz = tz

    async def handle(self, data: RecipeFullRequest):
        recipe = await self.recipe_service.create_recipe(data, tz=self.tz)
        await self.uow.commit()
        return recipe
