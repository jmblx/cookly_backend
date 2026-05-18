from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from application.recipe.common.exceptions import InvalidRecipeError
from application.recipe.common.service import RecipeService
from infrastructure.db.models import Recipe
from presentation.web_api.routes.recipe.schemas import RecipeStepRequest


@pytest.mark.asyncio
async def test_create_recipe_success(
    recipe_service: RecipeService,
    valid_recipe_request,
):
    result = await recipe_service.create_recipe(
        valid_recipe_request,
        ZoneInfo("UTC")
    )

    assert result["id"] == 1
    assert result["title"] == "Test recipe"


@pytest.mark.asyncio
async def test_create_recipe_invalid_duplicate_step_numbers(
    recipe_service: RecipeService,
    valid_recipe_request,
):
    valid_recipe_request.steps = [
        RecipeStepRequest(
            title="Step 1",
            description="Desc",
            number=1,
        ),
        RecipeStepRequest(
            title="Step 2",
            description="Desc",
            number=1,
        )
    ]

    with pytest.raises(InvalidRecipeError):
        await recipe_service.create_recipe(
            valid_recipe_request,
            ZoneInfo("UTC")
        )


@pytest.mark.asyncio
async def test_create_recipe_invalid_step_number_greater_than_count(
    recipe_service: RecipeService,
    valid_recipe_request,
):
    valid_recipe_request.steps = [
        RecipeStepRequest(
            title="Step 1",
            description="Desc",
            number=5,
        )
    ]

    with pytest.raises(InvalidRecipeError):
        await recipe_service.create_recipe(
            valid_recipe_request,
            ZoneInfo("UTC")
        )


@pytest.fixture
def existing_recipe():
    recipe = Recipe()

    recipe.id = 10
    recipe.author_id = uuid4()
    recipe.title = "Old title"

    return recipe


@pytest.mark.asyncio
async def test_update_recipe_success(
    recipe_service: RecipeService,
    existing_recipe,
    valid_recipe_request,
):
    result = await recipe_service.update_recipe(
        existing_recipe,
        valid_recipe_request,
    )

    assert result["id"] == 1
    assert result["title"] == "Test recipe"


@pytest.mark.asyncio
async def test_update_recipe_invalid_duplicate_steps(
    recipe_service: RecipeService,
    existing_recipe,
    valid_recipe_request,
):
    valid_recipe_request.steps = [
        RecipeStepRequest(
            title="Step 1",
            description="Desc",
            number=1,
        ),
        RecipeStepRequest(
            title="Step 2",
            description="Desc",
            number=1,
        )
    ]

    with pytest.raises(InvalidRecipeError):
        await recipe_service.update_recipe(
            existing_recipe,
            valid_recipe_request,
        )


@pytest.mark.asyncio
async def test_update_recipe_invalid_step_number(
    recipe_service: RecipeService,
    existing_recipe,
    valid_recipe_request,
):
    valid_recipe_request.steps = [
        RecipeStepRequest(
            title="Invalid",
            description="Desc",
            number=10,
        )
    ]

    with pytest.raises(InvalidRecipeError):
        await recipe_service.update_recipe(
            existing_recipe,
            valid_recipe_request,
        )
