
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from application.common.idp import IdentityProvider
from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from presentation.web_api.routes.recipe.schemas import DefaultRecipesResponse

moderator_router = APIRouter(
    prefix="",
    tags=["moderator"],
    route_class=DishkaRoute
)


@moderator_router.get(
    "/recipes/on-moderation",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "Published recipes",
        }
    }
)
async def get_user_published_recipes(
    recipe_reader: FromDishka[RecipeGateway],
    idp: FromDishka[IdentityProvider],
) -> DefaultRecipesResponse:
    await idp.get_moderator_or_raise()
    recipes = await recipe_reader.get_moderating_recipes()
    return DefaultRecipesResponse(
        recipes=recipes,
    )
