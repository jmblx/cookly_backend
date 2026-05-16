from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from application.recipe.categories.get_all import GetAllRecipeCategoriesHandler
from application.recipe.categories.search_category import SearchRecipeCategoryHandler
from presentation.web_api.routes.recipe.schemas import RecipeCategoryResponse

recipe_category_router = APIRouter(prefix="/recipe-category", tags=["recipe category"], route_class=DishkaRoute)


@recipe_category_router.get("/search", responses={
    status.HTTP_200_OK: {"description": "Founded most similar recipe categories"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
}
)
async def search_recipe_category(
    query: str,
    handler: FromDishka[SearchRecipeCategoryHandler]
) -> list[RecipeCategoryResponse]:
    return await handler.handle(query)


@recipe_category_router.get("/list", responses={
    status.HTTP_200_OK: {"description": "All recipe categories"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
}
)
async def get_all_recipe_categories(
    handler: FromDishka[GetAllRecipeCategoriesHandler]
) -> list[RecipeCategoryResponse]:
    return await handler.handle()
