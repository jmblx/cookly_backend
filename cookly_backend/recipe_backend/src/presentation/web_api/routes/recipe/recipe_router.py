from typing import Annotated

from dishka.integrations.fastapi import (
    DishkaRoute,
    FromDishka,
)
from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile
from pydantic import AnyHttpUrl
from starlette import status
from starlette.responses import Response

from application.common.idp import IdentityProvider
from application.recipe.add_to_favorite import SetRecipeIsFavoriteHandler
from application.recipe.create_recipe import CreateRecipeHandler
from application.recipe.delete_recipe import DeleteRecipeHandler
from application.recipe.get_recipe import GetRecipeHandler
from application.recipe.search_recipes import SearchRecipesHandler
from application.recipe.set_recipe_image import SetRecipeImageHandler
from application.recipe.set_recipe_rate import AddRecipeRateHandler
from application.recipe.set_recipe_step_image import SetRecipeStepImageHandler
from application.recipe.update_recipe import UpdateRecipeHandler
from infrastructure.db.models import Recipe
from presentation.web_api.routes.recipe.pub_recipe_request.schemas import RecipeRequestResponse
from presentation.web_api.routes.recipe.schemas import (
    DefaultRecipesResponse,
    ImagePathResponse,
    RecipeFullRequest,
    RecipeRequest,
    RecipeResponse,
    SearchRecipeQuery,
    UserRecipeResponse,
)

recipe_router = APIRouter(prefix="/recipe", tags=["recipe"], route_class=DishkaRoute)


@recipe_router.get(
    "/search",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {
            "description": "Returns founded recipes",
        }
    }
)
async def get_recipes_by_query(
    handler: FromDishka[SearchRecipesHandler],
    query: Annotated[SearchRecipeQuery, Query()]
) -> DefaultRecipesResponse:
    recipes = await handler.handle(
        query=query
    )
    return DefaultRecipesResponse(
        recipes=recipes,
    )


@recipe_router.post("", responses={
        status.HTTP_201_CREATED: {"description": "Created recipe data"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def create_recipe(
    data: RecipeRequest,
    idp: FromDishka[IdentityProvider],
    handler: FromDishka[CreateRecipeHandler]
) -> RecipeResponse:
    user_id = await idp.get_current_user_id()
    full_data = RecipeFullRequest(**data.model_dump(), author_id=user_id)
    recipe: Recipe = await handler.handle(full_data)
    return RecipeResponse.model_validate(recipe)


@recipe_router.put(
    "/{recipe_id}",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": "Updated recipe data"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def update_recipe(
    recipe_id: int,
    data: RecipeRequest,
    idp: FromDishka[IdentityProvider],
    handler: FromDishka[UpdateRecipeHandler]
) -> RecipeResponse:
    user_id = await idp.get_current_user_id()
    full_data = RecipeFullRequest(**data.model_dump(), author_id=user_id)
    recipe: Recipe = await handler.handle(recipe_id, full_data)
    return RecipeResponse.model_validate(recipe)


@recipe_router.delete(
    "/{recipe_id}",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Deleted"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def delete_recipe(
    handler: FromDishka[DeleteRecipeHandler],
    recipe_id: int,
    response: Response
):
    await handler.handle(recipe_id)
    response.status_code = status.HTTP_204_NO_CONTENT


@recipe_router.post("/{recipe_id}/avatar",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": "image path"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Cannot set image for recipe that is not yours"},
    }
)
async def set_recipe_image(
    handler: FromDishka[SetRecipeImageHandler],
    recipe_id: int,
    file: UploadFile = File(...),
) -> ImagePathResponse:
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл не был передан")

    content = await file.read()

    image_path = await handler.handle(
        content, recipe_id
    )

    return ImagePathResponse(image_path=AnyHttpUrl(image_path))


@recipe_router.post("/{recipe_id}/{recipe_step_number}/avatar",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_200_OK: {"description": "image path"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Cannot set image for recipe step that is not yours"},
    }
)
async def set_recipe_step_image(
    handler: FromDishka[SetRecipeStepImageHandler],
    recipe_id: int,
    recipe_step_number: int,
    file: UploadFile = File(...),
) -> ImagePathResponse:
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл не был передан")

    content = await file.read()

    image_path = await handler.handle(
        content, recipe_id, recipe_step_number
    )

    return ImagePathResponse(image_path=AnyHttpUrl(image_path))


@recipe_router.get(
    "/{recipe_id}",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={status.HTTP_200_OK: {"description": "recipe data"}},
)
async def get_recipe_by_id(
    handler: FromDishka[GetRecipeHandler],
    idp: FromDishka[IdentityProvider],
    recipe_id: int
) -> UserRecipeResponse:
    recipe, user_data, pub_recipe_request, existed_cooking_session = await handler.handle(recipe_id)
    user_id = await idp.get_current_user_id(ok_unauthorized=True)
    return UserRecipeResponse(
        recipe=RecipeResponse.model_validate(recipe),
        is_favorite=user_data.is_favorite if user_data else False,
        user_rate=user_data.rate if user_data else None,
        existed_cooking_session=existed_cooking_session,
        is_author=user_id==recipe.author_id,
        pub_recipe_request=RecipeRequestResponse.model_validate(pub_recipe_request) if pub_recipe_request else None,
    )


@recipe_router.put("/{recipe_id}/favorite",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Recipe added to favorites. No content return"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def set_recipe_is_favorite(
    handler: FromDishka[SetRecipeIsFavoriteHandler],
    recipe_id: int,
    is_favorite: Annotated[bool, Body()],
    response: Response
):
    await handler.handle(
        recipe_id, is_favorite=is_favorite
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@recipe_router.post("/{recipe_id}/set-rate",
    openapi_extra={
        "security": [{"BearerAuth": []}]
    },
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Recipe rate set. No content return"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    }
)
async def set_recipe_user_rate(
    handler: FromDishka[AddRecipeRateHandler],
    recipe_id: int,
    rate: Annotated[int, Body()],
    response: Response
):
    await handler.handle(
        recipe_id, rate
    )
    response.status_code = status.HTTP_204_NO_CONTENT
