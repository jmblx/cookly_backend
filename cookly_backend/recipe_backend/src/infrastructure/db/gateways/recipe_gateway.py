from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from domain.entities.value_objects import RECIPE_MODERATOR_ROLES, PubRecipeRequestStatus
from infrastructure.db.models import (
    CookingSession,
    PubRecipeRequest,
    Recipe,
    RecipeCategory,
    RecipeIngredient,
    RecipeStep,
    User,
    UserRecipe,
)

RecipeWithRelations = tuple[
    Recipe, UserRecipe | None, PubRecipeRequest | None, bool
]


CATEGORY_SIMILARITY_THRESHOLD = 0.2


class RecipeGateway:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, recipe: Recipe) -> None:
        self.session.add(recipe)
        await self.session.flush()

    async def get_by_id(self, recipe_id):
        return await self.session.get(Recipe, recipe_id)

    async def get_full_recipe_data(self, recipe_id) -> Recipe:
        stmt = select(Recipe).where(Recipe.id == recipe_id).options(
            selectinload(Recipe.steps),
            selectinload(Recipe.recipe_ingredients)
            .selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.recipe_categories),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_with_relations(self, recipe_id: int, user_id: UUID) -> RecipeWithRelations:
        user = await self.session.get(User, user_id)
        is_moderator_or_admin = user.role in RECIPE_MODERATOR_ROLES

        result = await self.session.execute(
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(
                selectinload(Recipe.steps),
                selectinload(Recipe.recipe_ingredients)
                .selectinload(RecipeIngredient.ingredient),
                selectinload(Recipe.recipe_categories),

                selectinload(Recipe.recipe_users),
                with_loader_criteria(
                    UserRecipe,
                    UserRecipe.user_id == user_id,
                    include_aliases=True
                ),

                selectinload(Recipe.recipe_cooking_sessions),
                with_loader_criteria(
                    CookingSession,
                    CookingSession.user_id == user_id
                )
            )
        )

        recipe = result.scalar_one()

        if recipe.updated_at is not None:
            reviewed_condition = PubRecipeRequest.reviewed_at > recipe.updated_at
        else:
            reviewed_condition = True

        pub_request_conditions = or_(
            and_(
                PubRecipeRequest.author_id == user_id,
                or_(
                    PubRecipeRequest.status == PubRecipeRequestStatus.pending.value,
                    and_(
                        PubRecipeRequest.status.in_([
                            PubRecipeRequestStatus.approved.value,
                            PubRecipeRequestStatus.rejected.value
                        ]),
                        reviewed_condition
                    )
                )
            ),
            *([PubRecipeRequest.status == PubRecipeRequestStatus.pending.value] if is_moderator_or_admin else [])
        )

        pub_requests_result = await self.session.execute(
            select(PubRecipeRequest)
            .where(
                PubRecipeRequest.recipe_id == recipe_id,
                pub_request_conditions
            )
            .order_by(PubRecipeRequest.created_at.desc())
        )
        pub_requests = pub_requests_result.scalars().all()

        user_data = recipe.recipe_users[0] if recipe.recipe_users else None
        pub_request_data = pub_requests[0] if pub_requests else None
        existed_cooking_session = bool(recipe.recipe_cooking_sessions)

        return recipe, user_data, pub_request_data, existed_cooking_session

    async def get_step_by_number(self, recipe_id, number) -> RecipeStep | None:
        recipe = (await self.session.execute(
            select(Recipe).where(Recipe.id == recipe_id).options(selectinload(Recipe.steps))
        )).scalar_one()
        for step in recipe.steps:
            if step.number == number:
                return step

    async def search_categories(self, query: str, limit: int = 20):
        ts_query = func.plainto_tsquery("russian", query)

        stmt = (
            select(RecipeCategory)
            .where(
                or_(
                    RecipeCategory.search_vector.op("@@")(ts_query),
                    func.similarity(RecipeCategory.title, query) > CATEGORY_SIMILARITY_THRESHOLD
                )
            )
            .order_by(
                func.ts_rank_cd(RecipeCategory.search_vector, ts_query).desc(),
                func.similarity(RecipeCategory.title, query).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_recipe_categories(self) -> Sequence[RecipeCategory]:
        stmt = select(RecipeCategory)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_moderating_recipes(self) -> list[Recipe]:
        pending_subq = (
            select(1)
            .where(
                PubRecipeRequest.recipe_id == Recipe.id,
                PubRecipeRequest.status == PubRecipeRequestStatus.pending.value
            )
        )

        stmt = (
            select(Recipe)
            .where(
                Recipe.is_public.is_(False),
                exists(pending_subq)
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, recipe: Recipe) -> None:
        await self.session.delete(recipe)
        await self.session.flush()
