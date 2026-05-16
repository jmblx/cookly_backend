from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Float, cast, func, insert, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.common.errors.exceptions import PermissionDeniedError
from application.common.interfaces.uow import Uow
from application.recipe.common.exceptions import InvalidRecipeError, RecipeNotFoundError
from infrastructure.db.gateways.ingredient_gateway import IngredientGateway
from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from infrastructure.db.models import Ingredient, IngredientGroup, Recipe, RecipeIngredient, RecipeStep
from infrastructure.db.models.secondary import recipe_recipe_category
from presentation.web_api.routes.recipe.schemas import RecipeFullRequest, SearchRecipeQuery

SEARCH_RECIPE_TRGRM_THRESHOLD = 0.06


class RecipeService:
    def __init__(
        self,
        session: AsyncSession,
        gateway: RecipeGateway,
        ingredient_gateway: IngredientGateway,
        uow: Uow,
        tz: ZoneInfo,
    ):
        self.session = session
        self.gateway = gateway
        self.ingredient_gateway = ingredient_gateway
        self.uow = uow
        self.tz = tz

    async def create_recipe(self, recipe_data: RecipeFullRequest, tz: ZoneInfo):
        from datetime import datetime
        recipe = Recipe(
            title=recipe_data.title,
            description=recipe_data.description,
            author_id=recipe_data.author_id,
            estimated_time=recipe_data.estimated_time,
            calories_by_100grams=recipe_data.calories_by_100grams,
            meal_time=recipe_data.meal_time.value,
            spicy_level=recipe_data.spicy_level,
            difficulty_level=recipe_data.difficulty_level,
            created_at=datetime.now(tz),
        )
        await self.gateway.save(recipe)

        for ing_data in recipe_data.recipe_ingredients:
            if not ing_data.unit_measurement:
                ingredient_default_unit_measurement = await self.ingredient_gateway.get_default_unit_measurement(
                    ing_data.ingredient_id
                )
                ing_data.unit_measurement = ingredient_default_unit_measurement

            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                **ing_data.model_dump()
            )
            self.session.add(recipe_ingredient)

        step_numbers, steps_amount = set(), len(recipe_data.steps)

        for step_data in recipe_data.steps:
            if step_data.number > steps_amount:
                raise InvalidRecipeError("Step number is greater than steps amount")
            if step_data.number in step_numbers:
                raise InvalidRecipeError("Step number is already in use")
            step = RecipeStep(
                recipe_id=recipe.id,
                **step_data.model_dump()
            )
            self.session.add(step)
            step_numbers.add(step_data.number)
        await self.uow.flush()

        await self.session.execute(
            insert(recipe_recipe_category).values([
                {"recipe_id": recipe.id, "recipe_category_id": cat_id}
                for cat_id in recipe_data.recipe_categories_ids
            ])
        )
        await self.gateway.save(recipe)

        return await self.gateway.get_full_recipe_data(recipe.id)

    async def update_recipe(self, recipe: Recipe, recipe_data: RecipeFullRequest):
        recipe_id = recipe.id

        recipe.title = recipe_data.title
        recipe.description = recipe_data.description
        recipe.author_id = recipe_data.author_id
        recipe.estimated_time = recipe_data.estimated_time
        recipe.calories_by_100grams = recipe_data.calories_by_100grams
        recipe.meal_time = recipe_data.meal_time.value
        recipe.is_public = False
        recipe.updated_at = datetime.now(self.tz)

        await self.session.flush()

        await self.session.execute(
            RecipeIngredient.__table__.delete().where(
                RecipeIngredient.recipe_id == recipe_id
            )
        )

        await self.session.execute(
            RecipeStep.__table__.delete().where(
                RecipeStep.recipe_id == recipe_id
            )
        )

        await self.session.execute(
            recipe_recipe_category.delete().where(
                recipe_recipe_category.c.recipe_id == recipe_id
            )
        )

        for ing_data in recipe_data.recipe_ingredients:
            if not ing_data.unit_measurement:
                ing_data.unit_measurement = await self.ingredient_gateway.get_default_unit_measurement(
                    ing_data.ingredient_id
                )

            self.session.add(
                RecipeIngredient(
                    recipe_id=recipe_id,
                    **ing_data.model_dump()
                )
            )

        step_numbers, steps_amount = set(), len(recipe_data.steps)

        for step_data in recipe_data.steps:
            if step_data.number > steps_amount:
                raise InvalidRecipeError("Step number is greater than steps amount")
            if step_data.number in step_numbers:
                raise InvalidRecipeError("Step number is already in use")

            self.session.add(
                RecipeStep(
                    recipe_id=recipe_id,
                    **step_data.model_dump()
                )
            )
            step_numbers.add(step_data.number)

        await self.uow.flush()

        await self.session.execute(
            insert(recipe_recipe_category).values([
                {"recipe_id": recipe_id, "recipe_category_id": cat_id}
                for cat_id in recipe_data.recipe_categories_ids
            ])
        )

        return await self.gateway.get_full_recipe_data(recipe_id)

    def _build_filters(self, query_data, exclude_group_ids):
        conditions = []

        if query_data.max_spicy is not None:
            conditions.append(Recipe.spicy_level <= query_data.max_spicy)

        if query_data.max_difficulty is not None:
            conditions.append(Recipe.difficulty_level <= query_data.max_difficulty)

        if query_data.max_calories_by_100grams is not None:
            conditions.append(Recipe.calories_by_100grams <= query_data.max_calories_by_100grams)

        if query_data.meal_time_type is not None:
            if isinstance(query_data.meal_time_type, list):
                mtts = [mtt.value for mtt in query_data.meal_time_type]
                conditions.append(Recipe.meal_time.in_(mtts))
            else:
                conditions.append(Recipe.meal_time == query_data.meal_time_type.value)

        if query_data.min_avg_rating is not None:
            avg_rating = func.coalesce(
                Recipe.rating_sum / func.nullif(Recipe.rating_count, 0), 0
            )
            conditions.append(avg_rating >= query_data.min_avg_rating)

        if query_data.max_estimated_cooking_time is not None:
            conditions.append(Recipe.estimated_time <= query_data.max_estimated_cooking_time)

        if exclude_group_ids:
            exclude_subquery = (
                select(RecipeIngredient.recipe_id)
                .join(Ingredient)
                .join(IngredientGroup, Ingredient.ingredient_groups)
                .where(IngredientGroup.id.in_(exclude_group_ids))
            )
            conditions.append(Recipe.id.not_in(exclude_subquery))

        return conditions

    def _build_text_search(self, query: str | None):
        if not query or not query.strip():
            return None, False

        ts_query = func.plainto_tsquery("russian", query)
        similarity_score = func.similarity(Recipe.title, query)

        weights = [0.4, 0.25, 0.1, 0.27]
        weights_str = "{" + ",".join(map(str, weights)) + "}"

        rank_expr = func.ts_rank(
            text(f"'{weights_str}'::float4[]"),
            Recipe.search_vector,
            ts_query
        )

        text_rank = func.greatest(rank_expr, similarity_score * 2)

        condition = or_(
            Recipe.search_vector.op("@@")(ts_query),
            similarity_score > SEARCH_RECIPE_TRGRM_THRESHOLD
        )

        return (text_rank, condition), True

    def _build_group_filter(self, include_group_ids):
        if not include_group_ids:
            return None, None, False

        has_group_sub = (
            select(RecipeIngredient.recipe_id)
            .join(Ingredient)
            .join(IngredientGroup, Ingredient.ingredient_groups)
            .where(IngredientGroup.id.in_(include_group_ids))
        )

        group_count_subq = (
            select(func.count(func.distinct(IngredientGroup.id)))
            .select_from(RecipeIngredient)
            .join(Ingredient)
            .join(IngredientGroup, Ingredient.ingredient_groups)
            .where(RecipeIngredient.recipe_id == Recipe.id)
            .where(IngredientGroup.id.in_(include_group_ids))
            .correlate(Recipe)
            .scalar_subquery()
        )

        return has_group_sub, group_count_subq, True

    def _build_level_scores(self, query_data):
        spicy_score = None
        difficulty_score = None

        if query_data.max_spicy:
            spicy_score = cast(Recipe.spicy_level, Float) / float(query_data.max_spicy)

        if query_data.max_difficulty:
            difficulty_score = cast(Recipe.difficulty_level, Float) / float(query_data.max_difficulty)

        return spicy_score, difficulty_score

    def _build_ordering(
        self,
        text_data,
        has_text,
        group_expr,
        has_groups,
        spicy_score,
        difficulty_score
    ):
        order_parts = []

        if has_text:
            text_rank, text_condition = text_data
            order_parts.append(text_rank)

        if has_groups:
            order_parts.append(group_expr * 0.5)

        coef = 0.1 if has_text else 0.3

        if spicy_score is not None:
            order_parts.append(spicy_score * coef)

        if difficulty_score is not None:
            order_parts.append(difficulty_score * coef)

        if not order_parts:
            return Recipe.created_at.desc()

        expr = order_parts[0]
        for part in order_parts[1:]:
            expr = expr + part

        return expr.desc()

    async def search_recipes(
        self,
        query_data: SearchRecipeQuery,
        exclude_ingredient_group_ids: list[int] | None = None,
    ):
        conditions = self._build_filters(query_data, exclude_ingredient_group_ids)

        text_data, has_text = self._build_text_search(query_data.query)
        if has_text:
            text_rank, text_condition = text_data
            conditions.append(text_condition)

        has_group_sub, group_expr, has_groups = self._build_group_filter(
            query_data.include_ingredient_group_ids
        )

        if has_groups:
            conditions.append(Recipe.id.in_(has_group_sub))

        spicy_score, difficulty_score = self._build_level_scores(query_data)

        stmt = select(Recipe).where(*conditions)

        order_expr = self._build_ordering(
            text_data,
            has_text,
            group_expr,
            has_groups,
            spicy_score,
            difficulty_score
        )

        stmt = stmt.order_by(order_expr)
        stmt = stmt.limit(query_data.limit).offset(query_data.offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def load_recipes_ingredients(
        self,
        recipe_ids: list[int]
    ) -> dict[int, list[str]]:
        if not recipe_ids:
            return {}

        session = self.session

        stmt = (
            select(Recipe)
            .where(Recipe.id.in_(recipe_ids))
            .options(
                selectinload(Recipe.recipe_ingredients)
                .selectinload(RecipeIngredient.ingredient)
            )
        )

        result = await session.execute(stmt)
        recipes = result.scalars().unique().all()

        ingredients_map = {}
        for recipe in recipes:
            ingredients_map[recipe.id] = [
                ri.ingredient.title
                for ri in recipe.recipe_ingredients
                if ri.ingredient
            ]

        return ingredients_map

    async def get_with_author_check(self, recipe_id: int, user_id: UUID):
        recipe = await self.gateway.get_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundError
        if recipe.author_id != user_id:
            raise PermissionDeniedError("You do not have permission to change this recipe")
        return recipe
