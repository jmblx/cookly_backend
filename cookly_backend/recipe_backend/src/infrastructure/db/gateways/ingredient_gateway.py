from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, exists, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.recipe.common.exceptions import InvalidRecipeError
from infrastructure.db.models import Ingredient, IngredientGroup, ingredient_ingredient_group, user_ingredient_group

INGREDIENT_SIMILARITY_THRESHOLD = 0.2


class IngredientGateway:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, ingredient: Ingredient) -> None:
        self.session.add(ingredient)
        await self.session.flush()

    async def get_by_id(self, ingredient_id: int) -> Ingredient | None:
        return await self.session.get(Ingredient, ingredient_id)

    async def get_default_unit_measurement(self, ingredient_id) -> str:
        ingredient = await self.get_by_id(ingredient_id)
        if not ingredient:
            raise InvalidRecipeError(f"Ingredient with id {ingredient_id} not found")
        if not ingredient.default_unit_measurement:
            raise InvalidRecipeError(
                f"Ingredient {ingredient.title} has no default "
                "unit measurement and no unit measurement provided"
            )
        return ingredient.default_unit_measurement

    async def search_ingredients(self, query: str, limit: int = 20):
        ts_query = func.plainto_tsquery("russian", query)

        stmt_fts = (
            select(Ingredient)
            .where(Ingredient.search_vector.op("@@")(ts_query))
            .order_by(
                func.ts_rank_cd(Ingredient.search_vector, ts_query).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt_fts)
        rows = result.scalars().all()

        if rows:
            return rows

        stmt_trgm = (
            select(Ingredient)
            .where(
                func.similarity(Ingredient.title, query) > INGREDIENT_SIMILARITY_THRESHOLD
            )
            .order_by(
                func.similarity(Ingredient.title, query).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt_trgm)
        return result.scalars().all()

    async def get_all_ingredient_groups(self) -> Sequence[IngredientGroup]:
        stmt = select(IngredientGroup).join(
            ingredient_ingredient_group,
            IngredientGroup.id == ingredient_ingredient_group.c.ingredient_group_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_ingredient_groups_with_user_selected_data(
        self,
        user_id: UUID | None = None
    ) -> list[dict[str, IngredientGroup | bool]]:
        ig = IngredientGroup
        uig = user_ingredient_group

        if user_id:
            is_selected = exists(
                select(1).where(
                    and_(
                        uig.c.user_id == user_id,
                        uig.c.ingredient_group_id == ig.id
                    )
                )
            )
        else:
            is_selected = literal(value=False)

        stmt = select(
            ig,
            is_selected.label("is_selected")
        )

        result = await self.session.execute(stmt)

        return [
            {
                "group": row[0],
                "is_excluded_by_user": row[1]
            }
            for row in result.all()
        ]
