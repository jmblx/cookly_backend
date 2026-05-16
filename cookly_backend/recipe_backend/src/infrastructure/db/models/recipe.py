import typing
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text, Uuid
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.value_objects import MealTimeType
from infrastructure.db.models import Base
from infrastructure.db.models.common import added_at, datetime_tz, intpk

if typing.TYPE_CHECKING:
    from infrastructure.db.models import (
        CookingSession,
        PubRecipeRequest,
        RecipeCategory,
        RecipeIngredient,
        User,
        UserRecipe,
    )


class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[intpk]
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text, nullable=True)
    author_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("user.id"))
    estimated_time: Mapped[int] = mapped_column(Numeric, nullable=True)
    calories_by_100grams: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    meal_time: Mapped[MealTimeType] = mapped_column(String(30))
    rating_sum: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), default=0)
    rating_count: Mapped[int] = mapped_column(default=0)
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)
    spicy_level: Mapped[int] = mapped_column(default=0)
    difficulty_level: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[added_at]
    updated_at: Mapped[datetime_tz]

    author: Mapped["User"] = relationship("User", back_populates="created_recipes")
    steps: Mapped[list["RecipeStep"]] = relationship(
        "RecipeStep",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    pub_requests: Mapped[list["PubRecipeRequest"]] = relationship(
        "PubRecipeRequest",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    ingredients = association_proxy("recipe_ingredients", "ingredient")
    recipe_cooking_sessions: Mapped[list["CookingSession"]] = relationship(
        "CookingSession", back_populates="recipe", cascade="all, delete-orphan"
    )
    recipe_users: Mapped[list["UserRecipe"]] = relationship(
        "UserRecipe",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )
    recipe_categories: Mapped[list["RecipeCategory"]] = relationship(
        secondary="recipe_recipe_category",
        back_populates="recipes",
        passive_deletes=True
    )
    search_vector = mapped_column(TSVECTOR)

    __table_args__ = (
        Index(
            "ix_recipe_search_vector",
            "search_vector",
            postgresql_using="gin"
        ),
        Index(
            "ix_recipe_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"}
        ),
    )

    def __repr__(self):
        return f"<Recipe {self.id}: {self.title}>"


class RecipeStep(Base):
    __tablename__ = "recipe_step"

    id: Mapped[intpk]
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text, nullable=True)
    number: Mapped[int]
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipe.id", ondelete="CASCADE"))

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="steps")

    def __repr__(self):
        return f"<Step {self.id}: {self.title} Recipe {self.recipe_id}>"
