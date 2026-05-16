from application.common.errors.exceptions import PermissionDeniedError
from application.common.idp import IdentityProvider
from application.common.interfaces.s3_storage import S3Storage
from application.recipe.common.exceptions import RecipeNotFoundError
from infrastructure.db.gateways.recipe_gateway import RecipeGateway


class SetRecipeImageHandler:
    def __init__(self, recipe_gateway: RecipeGateway, idp: IdentityProvider, minio_service: S3Storage):
        self.recipe_gateway = recipe_gateway
        self.idp = idp
        self.minio_service = minio_service

    async def handle(self, content: bytes, recipe_id: int):
        # проверка прав на рецепт
        recipe = await self.recipe_gateway.get_by_id(recipe_id)
        if recipe is None:
            raise RecipeNotFoundError
        if recipe.author_id != await self.idp.get_current_user_id():
            raise PermissionDeniedError
        return await self.minio_service.set_recipe_image(content, str(recipe_id))
