from uuid import uuid4
from zoneinfo import ZoneInfo
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.interfaces.uow import Uow
from application.recipe.common.service import RecipeService
from domain.entities.value_objects import MealTimeType
from infrastructure.db.gateways.ingredient_gateway import IngredientGateway
from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from presentation.web_api.routes.recipe.schemas import (
    RecipeFullRequest,
    RecipeIngredientRequest,
    RecipeStepRequest,
)


class TestProvider(Provider):

    @provide(scope=Scope.APP)
    def provide_session(self) -> AsyncSession:
        session = AsyncMock()

        execute_result = AsyncMock()
        execute_result.scalars.return_value.all.return_value = []

        session.execute.return_value = execute_result
        session.flush = AsyncMock()

        return session

    @provide(scope=Scope.APP)
    def provide_gateway(self) -> RecipeGateway:
        gateway = AsyncMock()

        async def save_side_effect(recipe):
            if not recipe.id:
                recipe.id = 1

        gateway.save.side_effect = save_side_effect

        gateway.get_full_recipe_data.return_value = {
            "id": 1,
            "title": "Test recipe"
        }

        return gateway

    @provide(scope=Scope.APP)
    def provide_ingredient_gateway(self) -> IngredientGateway:
        gateway = AsyncMock()
        gateway.get_default_unit_measurement.return_value = "g"
        return gateway

    @provide(scope=Scope.APP)
    def provide_uow(self) -> Uow:
        uow = AsyncMock()
        uow.flush = AsyncMock()
        return uow

    @provide(scope=Scope.APP)
    def provide_tz(self) -> ZoneInfo:
        return ZoneInfo("UTC")

    @provide(scope=Scope.APP)
    def provide_service(
        self,
        session: AsyncSession,
        gateway: RecipeGateway,
        ingredient_gateway: IngredientGateway,
        uow: Uow,
        tz: ZoneInfo,
    ) -> RecipeService:
        return RecipeService(
            session=session,
            gateway=gateway,
            ingredient_gateway=ingredient_gateway,
            uow=uow,
            tz=tz,
        )


@pytest_asyncio.fixture
async def container():
    container = make_async_container(TestProvider())
    yield container
    await container.close()


@pytest_asyncio.fixture
async def recipe_service(container):
    return await container.get(RecipeService)


@pytest_asyncio.fixture
async def session(container):
    return await container.get(AsyncMock)


@pytest.fixture
def valid_recipe_request():
    return RecipeFullRequest(
        title="Carbonara",
        description="Test description",
        author_id=uuid4(),
        estimated_time=30,
        calories_by_100grams=250.5,
        meal_time=MealTimeType.supper,
        spicy_level=2,
        difficulty_level=3,
        recipe_categories_ids=[1, 2],
        recipe_ingredients=[
            RecipeIngredientRequest(
                ingredient_id=1,
                quantity=100,
                unit_measurement=None,
            )
        ],
        steps=[
            RecipeStepRequest(
                title="Step 1",
                description="Cook pasta",
                number=1,
            )
        ]
    )
