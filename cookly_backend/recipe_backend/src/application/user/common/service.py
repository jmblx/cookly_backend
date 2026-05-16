import secrets
import string
import typing
from datetime import datetime
from typing import NamedTuple
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import and_, desc, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.errors.exceptions import NotFoundError
from application.common.interfaces.uow import Uow
from application.user.common.preference_service import PreferenceProfileService
from application.user.feed_utils import (
    ScoreConfig,
    apply_base_filters,
    apply_keyset_pagination,
    apply_meal_filter,
    build_total_score,
)
from domain.entities.value_objects import CookingSessionStatus
from infrastructure.db.gateways.ingredient_gateway import IngredientGateway
from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from infrastructure.db.gateways.user_gateway import UserGateway
from infrastructure.db.models import Recipe, RecipeIngredient
from infrastructure.db.models.secondary import (
    CookingSession,
    UserRecipe,
    ingredient_ingredient_group,
    user_ingredient_group,
)


class FeedData(NamedTuple):
    recipes: list[Recipe] | None
    last_recipe_score: float | None
    last_recipe_id: int | None
    pagination_key: str | None


def generate_pagination_key(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        gateway: UserGateway,
        ingredient_gateway: IngredientGateway,
        uow: Uow,
        recipe_gateway: RecipeGateway,
        tz: ZoneInfo,
        preference_service: PreferenceProfileService,
    ):
        self.session = session
        self.gateway = gateway
        self.ingredient_gateway = ingredient_gateway
        self.recipe_gateway = recipe_gateway
        self.uow = uow
        self.tz = tz
        self.preference_service = preference_service

    async def set_user_excluded_ingredient_groups(
        self,
        user_id: UUID,
        excluded_ingredient_groups: list[int]
    ):
        await self.session.execute(
            user_ingredient_group.delete().where(
                user_ingredient_group.c.user_id == user_id
            )
        )
        if not excluded_ingredient_groups:
            return
        await self.session.execute(
            insert(user_ingredient_group).values([
                {"user_id": user_id, "ingredient_group_id": group_id}
                for group_id in excluded_ingredient_groups
            ])
        )

    async def get_excluded_ingredient_groups_ids(
        self,
        user_id: UUID
    ) -> list[int]:
        stmt = select(user_ingredient_group.c.ingredient_group_id).where(
            user_ingredient_group.c.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return typing.cast(list[int], result.scalars().all())

    async def get_relevant_recipes(
        self,
        user_id: UUID,
        meal_time: str,
        last_score: float | None = None,
        last_id: int | None = None,
        pagination_key: str | None = None,
        limit: int = 20,
        config: ScoreConfig = ScoreConfig(),
    ) -> FeedData:
        pagination_key = pagination_key or generate_pagination_key()

        ri = RecipeIngredient
        ig = ingredient_ingredient_group

        excluded_group_ids = await self.get_excluded_ingredient_groups_ids(user_id)

        excluded_subq = (
            select(1)
            .select_from(ri)
            .join(ig, ig.c.ingredient_id == ri.ingredient_id)
            .where(
                and_(
                    ri.recipe_id == Recipe.id,
                    ig.c.ingredient_group_id.in_(excluded_group_ids)
                )
            )
        )

        preferences = await self.preference_service.get_profile(user_id)

        score = build_total_score(
            config,
            user_id=user_id,
            meal_time=meal_time,
            seed=pagination_key,
            preferences=preferences
        )

        stmt = select(Recipe, score.label("score"))

        stmt = apply_base_filters(stmt, user_id, excluded_subq)
        stmt = apply_meal_filter(stmt, meal_time, strict=config.strict_meal)
        stmt = apply_keyset_pagination(stmt, score, last_score, last_id)

        stmt = stmt.order_by(score.desc(), Recipe.id.desc()).limit(limit)

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return FeedData([], None, None, None)

        return FeedData(
            [row[0] for row in rows],
            rows[-1][1],
            rows[-1][0].id,
            pagination_key
        )

    async def get_or_create_user_recipe_record(self, user_id: UUID, recipe_id: int) -> UserRecipe:
        recipe = await self.recipe_gateway.get_by_id(recipe_id)
        if not recipe:
            raise NotFoundError(f"Recipe with id {recipe_id} not found")

        user_recipe_record = await self.gateway.get_user_recipe_record(user_id, recipe_id)

        if not user_recipe_record:
            user_recipe_record = UserRecipe(
                user_id=user_id,
                recipe=recipe,
                added_to_favorite_at=datetime.now(self.tz),
            )
            await self.gateway.save_user_recipe(user_recipe_record)
            await self.session.flush()

        await self.session.refresh(user_recipe_record, attribute_names=["recipe"])

        return user_recipe_record


    async def get_user_recipe_record_or_none(self, user_id: UUID, recipe_id: int) -> UserRecipe:
        recipe = await self.recipe_gateway.get_by_id(recipe_id)
        if not recipe:
            raise NotFoundError(f"Recipe with id {recipe_id} not found")

        return await self.gateway.get_user_recipe_record(user_id, recipe_id)

    async def set_recipe_favorite_value(self, user_recipe_record: UserRecipe, *, value: bool):
        user_recipe_record.is_favorite = value
        if value:
            user_recipe_record.added_to_favorite_at = datetime.now(tz=self.tz)
        else:
            user_recipe_record.added_to_favorite_at = None
        await self.gateway.save_user_recipe(user_recipe_record)

    async def set_user_recipe_rate(self, user_recipe_record: UserRecipe, rate: int):
        previous_rate = user_recipe_record.rate
        user_recipe_record.rate = rate

        if previous_rate is None:
            delta = rate
            count_delta = 1
        else:
            delta = rate - previous_rate
            count_delta = 0

        stmt = (
            update(Recipe)
            .where(Recipe.id == user_recipe_record.recipe_id)
            .values(
                rating_sum=Recipe.rating_sum + delta,
                rating_count=Recipe.rating_count + count_delta
            )
        )

        await self.session.execute(stmt)
        await self.gateway.save_user_recipe(user_recipe_record)

    async def check_is_author_recipe(self, user_id: UUID, recipe_id: int) -> bool:
        recipe = await self.recipe_gateway.get_by_id(recipe_id)
        return recipe.author_id == user_id

    async def get_recipes_history(self, user_id: UUID):
        cs = CookingSession
        r = Recipe

        stmt = (
            select(cs, r)
            .join(r, cs.recipe_id == r.id)
            .where(
                cs.user_id == user_id,
                cs.status.in_([
                    CookingSessionStatus.finished.value,
                    CookingSessionStatus.cancelled.value
                ])
            )
            .distinct(cs.recipe_id)
            .order_by(
                cs.recipe_id,
                desc(cs.end_time)  # или last_activity если end_time может быть NULL
            )
        )

        result = await self.session.execute(stmt)

        return [
            row[1]
            for row in result.all()
        ]

    async def get_favorite_recipes(self, user_id: UUID):
        r = Recipe
        ur = UserRecipe
        stmt = (
            select(r).join(ur, ur.recipe_id == r.id).where(
                ur.is_favorite == True, ur.user_id == user_id # noqa: E712
            ).order_by(ur.added_to_favorite_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().all()
