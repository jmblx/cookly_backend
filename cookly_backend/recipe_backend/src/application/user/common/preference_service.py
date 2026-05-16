from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models import CookingSession, Recipe
from infrastructure.db.models.secondary import recipe_recipe_category


class UserPreferenceProfile(BaseModel):
    difficulty: dict[int, float]
    spicy: dict[int, float]
    categories: dict[int, float]

    updated_at: datetime


def smooth_ratio(success: int, total: int) -> float:
    return (success + 3) / (total + 6)


class PreferenceProfileService:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis
    ):
        self.session = session
        self.redis = redis

    async def _calculate_number_recipe_attribute_preference(
        self,
        user_id: UUID,
        attribute,
    ):
        stmt = (
            select(
                attribute,
                func.count().label("total"),
                func.sum(
                    case(
                        (
                            CookingSession.status == "finished",
                            1
                        ),
                        else_=0
                    )
                ).label("success")
            )
            .join(
                Recipe,
                Recipe.id == CookingSession.recipe_id
            )
            .where(
                CookingSession.user_id == user_id,
                CookingSession.status.in_([
                    "finished",
                    "cancelled"
                ])
            )
            .group_by(
                attribute
            )
        )

        result = await self.session.execute(stmt)

        data = {}

        for level, total, success in result.all():
            data[level] = smooth_ratio(success, total)

        return data

    async def _get_difficulty_stats(
        self,
        user_id: UUID
    ) -> dict[int, float]:
        return await self._calculate_number_recipe_attribute_preference(user_id, Recipe.difficulty_level)

    async def _get_spicy_stats(
        self,
        user_id: UUID
    ) -> dict[int, float]:
        return await self._calculate_number_recipe_attribute_preference(user_id, Recipe.spicy_level)

    async def _get_category_stats(
        self,
        user_id: UUID
    ) -> dict[int, float]:

        stmt = (
            select(
                recipe_recipe_category.c.recipe_category_id,
                func.count().label("total"),
                func.sum(
                    case(
                        (CookingSession.status == "finished", 1),
                        else_=0
                    )
                ).label("success")
            )
            .join(
                Recipe,
                Recipe.id == recipe_recipe_category.c.recipe_id
            )
            .join(
                CookingSession,
                CookingSession.recipe_id == Recipe.id
            )
            .where(
                CookingSession.user_id == user_id,
                CookingSession.status.in_(["finished", "cancelled"])
            )
            .group_by(
                recipe_recipe_category.c.recipe_category_id
            )
        )

        result = await self.session.execute(stmt)

        data = {}

        for category_id, total, success in result.all():
            data[category_id] = smooth_ratio(success, total)

        return data

    async def recalculate(
        self,
        user_id: UUID
    ):
        difficulty = await self._get_difficulty_stats(user_id)
        spicy = await self._get_spicy_stats(user_id)
        categories = await self._get_category_stats(user_id)

        profile = UserPreferenceProfile(
            difficulty=difficulty,
            spicy=spicy,
            categories=categories,
            updated_at=datetime.now(UTC)
        )

        await self.redis.set(
            f"user:preferences:{user_id}",
            profile.model_dump_json(),
            ex=60 * 60 * 24
        )

        return profile

    async def get_profile(
        self,
        user_id: UUID
    ) -> UserPreferenceProfile | None:

        raw = await self.redis.get(
            f"user:preferences:{user_id}"
        )

        if not raw:
            return None

        return UserPreferenceProfile.model_validate_json(raw)


def build_difficulty_preference_score(
    profile: UserPreferenceProfile | None
):
    if not profile or not profile.difficulty:
        return 0.5

    return case(
        *[
            (
                Recipe.difficulty_level == int(level),
                value
            )
            for level, value in profile.difficulty.items()
        ],
        else_=0.5
    )

def build_spicy_preference_score(
    profile: UserPreferenceProfile | None
):
    if not profile or not profile.spicy:
        return 0.5

    return case(
        *[
            (
                Recipe.spicy_level == int(level),
                value
            )
            for level, value in profile.spicy.items()
        ],
        else_=0.5
    )


def build_category_preference_score(
    profile: UserPreferenceProfile | None
):
    if not profile or not profile.categories:
        return 0.5

    category_score_case = case(
        *[
            (
                recipe_recipe_category.c.recipe_category_id == category_id,
                value
            )
            for category_id, value in profile.categories.items()
        ],
        else_=None
    )

    subq = (
        select(func.avg(category_score_case))
        .select_from(recipe_recipe_category)
        .where(
            recipe_recipe_category.c.recipe_id == Recipe.id
        )
        .scalar_subquery()
    )

    return func.coalesce(subq, 0.5)
