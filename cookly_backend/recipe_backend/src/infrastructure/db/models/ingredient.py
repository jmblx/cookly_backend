from typing import TYPE_CHECKING

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from infrastructure.db.models import Base
from infrastructure.db.models.common import added_at, intpk

if TYPE_CHECKING:
    from infrastructure.db.models import IngredientGroup, RecipeIngredient


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[intpk]
    title: Mapped[str]
    default_unit_measurement: Mapped[str | None]
    created_at: Mapped[added_at]

    search_vector = mapped_column(TSVECTOR)

    ingredient_groups: Mapped[list["IngredientGroup"]] = relationship(
        secondary="ingredient_ingredient_group",
        back_populates="ingredients"
    )
    ingredient_recipes: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )
    recipes = association_proxy("ingredient_recipes", "recipe")

    __table_args__ = (
        Index(
            "ix_ingredient_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"}
        ),
        Index(
            "ix_ingredient_search_vector",
            "search_vector",
            postgresql_using="gin"
        ),
    )

    def __repr__(self):
        return f"<Ingredient {self.id}: {self.title}>"
