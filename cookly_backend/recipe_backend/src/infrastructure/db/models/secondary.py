import typing
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Numeric, String, Table
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from domain.entities.value_objects import CookingSessionStatus
from infrastructure.db.models import Base
from infrastructure.db.models.common import added_at, datetime_tz, intpk
from infrastructure.db.models.ingredient import Ingredient
from infrastructure.db.models.recipe import Recipe

if typing.TYPE_CHECKING:
    from infrastructure.db.models import User



class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipe.id", ondelete="CASCADE"),
        primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredient.id", ondelete="CASCADE"),
        primary_key=True
    )
    unit_measurement: Mapped[str]
    quantity: Mapped[float] = mapped_column(Numeric(10, 2))

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="ingredient_recipes")

    def __repr__(self) -> str:
        return f"<RecipeIngredient {self.recipe_id} - {self.ingredient_id}>"


class CookingSession(Base): # relationships
    __tablename__ = "cooking_session"

    id: Mapped[intpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    last_activity: Mapped[datetime_tz]
    current_step: Mapped[int] = mapped_column(default=1)
    start_time: Mapped[added_at]
    end_time: Mapped[datetime_tz]
    status: Mapped[CookingSessionStatus] = mapped_column(String(30), default=CookingSessionStatus.active.value)

    user: Mapped["User"] = relationship("User", back_populates="cooking_sessions")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_cooking_sessions")

    def __repr__(self):
        return f"<CookingSession {self.id}: user {self.user_id}, recipe {self.recipe_id}>"


user_ingredient_group = Table(
    "user_ingredient_group",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_group_id", ForeignKey("ingredient_group.id", ondelete="CASCADE"), primary_key=True),
)


ingredient_ingredient_group = Table(
    "ingredient_ingredient_group",
    Base.metadata,
    Column("ingredient_id", ForeignKey("ingredient.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_group_id", ForeignKey("ingredient_group.id", ondelete="CASCADE"), primary_key=True),
)


recipe_recipe_category = Table(
    "recipe_recipe_category",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True),
    Column("recipe_category_id", ForeignKey("recipe_category.id", ondelete="CASCADE"), primary_key=True),
)


class UserRecipe(Base):
    __tablename__ = "user_recipe"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True)
    is_favorite: Mapped[bool] = mapped_column(default=False)
    rate: Mapped[int] = mapped_column(nullable=True)
    review: Mapped[str] = mapped_column(nullable=True)
    added_to_favorite_at: Mapped[datetime_tz]

    user: Mapped["User"] = relationship("User", back_populates="user_recipes")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_users")

    def __repr__(self):
        return f"<UserRecipe {self.id}: user {self.user_id}, recipe {self.recipe_id}>"
