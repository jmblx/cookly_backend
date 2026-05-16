from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from application.ingredient.search_ingredients import SearchIngredientsHandler
from presentation.web_api.routes.recipe.schemas import IngredientResponse

ingredient_router = APIRouter(prefix="/ingredient", tags=["ingredient"], route_class=DishkaRoute)


@ingredient_router.get("/search", responses={
    status.HTTP_200_OK: {"description": "Founded most similar ingredients"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
}
)
async def search_ingredient(
    query: str,
    handler: FromDishka[SearchIngredientsHandler]
) -> list[IngredientResponse]:
    return await handler.handle(query)
