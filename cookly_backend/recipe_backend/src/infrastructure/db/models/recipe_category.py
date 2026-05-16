import typing

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from infrastructure.db.models import Base
from infrastructure.db.models.common import intpk

if typing.TYPE_CHECKING:
    from infrastructure.db.models import Recipe

class RecipeCategory(Base):
    __tablename__ = "recipe_category"

    id: Mapped[intpk]
    title: Mapped[str]

    search_vector = mapped_column(TSVECTOR)

    recipes: Mapped[list["Recipe"]] = relationship(
        secondary="recipe_recipe_category",
        back_populates="recipe_categories"
    )

    __table_args__ = (
        Index(
            "ix_recipe_category_search_vector",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"}
        ),
        Index(
            "ix_recipe_category_title_trgm",
            "search_vector",
            postgresql_using="gin"
        ),
    )

    def __repr__(self):
        return f"<RecipeCategory {self.id}: {self.title}>"
