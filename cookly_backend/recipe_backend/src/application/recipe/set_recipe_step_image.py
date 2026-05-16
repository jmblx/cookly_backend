from application.common.errors.exceptions import PermissionDeniedError
from application.common.idp import IdentityProvider
from application.common.interfaces.s3_storage import S3Storage
from application.recipe.common.exceptions import RecipeNotFoundError, RecipeStepNotFoundError
from infrastructure.db.gateways.recipe_gateway import RecipeGateway


class SetRecipeStepImageHandler:
    def __init__(self, recipe_gateway: RecipeGateway, idp: IdentityProvider, minio_service: S3Storage):
        self.recipe_gateway = recipe_gateway
        self.idp = idp
        self.minio_service = minio_service

    async def handle(self, content: bytes, recipe_id: int, recipe_step_number: int) -> str:
        recipe = await self.recipe_gateway.get_by_id(recipe_id)
        if recipe is None:
            raise RecipeNotFoundError
        if recipe.author_id != await self.idp.get_current_user_id():
            raise PermissionDeniedError
        if (recipe_step := await self.recipe_gateway.get_step_by_number(recipe_id, recipe_step_number)) is None:
            raise RecipeStepNotFoundError
        return await self.minio_service.set_recipe_step_image(content, str(recipe_step.id))
