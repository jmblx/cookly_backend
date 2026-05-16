from uuid import UUID

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.value_objects import PubRecipeRequestStatus
from infrastructure.db.models import PubRecipeRequest, Recipe, UserRecipe
from infrastructure.db.models.user import User


class UserGateway:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, user: User) -> None:
        self.session.add(user)
        await self.session.flush()

    async def get_user_recipe_record(self, user_id: UUID, recipe_id: int) -> UserRecipe | None:
        stmt = select(UserRecipe).where(UserRecipe.user_id == user_id, UserRecipe.recipe_id == recipe_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_user_recipe(self, user_recipe: UserRecipe) -> None:
        self.session.add(user_recipe)
        await self.session.flush()

    async def get_user_saved_recipes(self, user_id: UUID) -> list[Recipe]:
        pending_subq = (
            select(1)
            .where(
                PubRecipeRequest.recipe_id == Recipe.id,
                or_(
                    PubRecipeRequest.created_at > Recipe.updated_at,
                    PubRecipeRequest.status == PubRecipeRequestStatus.pending.value
                ),
            )
        )

        stmt = (
            select(Recipe)
            .where(
                Recipe.author_id == user_id,
                Recipe.is_public.is_(False),
                ~exists(pending_subq),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_moderating_recipes(self, user_id: UUID) -> list[Recipe]:
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
                Recipe.author_id == user_id,
                Recipe.is_public.is_(False),
                exists(pending_subq)
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_rejected_recipes(self, user_id: UUID) -> list[Recipe]:
        last_status_subq = (
            select(PubRecipeRequest.status)
            .where(
                PubRecipeRequest.recipe_id == Recipe.id,
                Recipe.updated_at < PubRecipeRequest.reviewed_at
            )
            .order_by(PubRecipeRequest.created_at.desc())
            .limit(1)
            .scalar_subquery()
        )

        stmt = (
            select(Recipe)
            .where(
                Recipe.author_id == user_id,
                Recipe.is_public.is_(False),
                last_status_subq == PubRecipeRequestStatus.rejected.value,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_published_recipes(self, user_id: UUID) -> list[Recipe]:
        stmt = (
            select(Recipe)
            .where(
                Recipe.author_id == user_id,
                Recipe.is_public.is_(True)
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
