import typing

from sqlalchemy.orm import (
    Mapped,
    relationship,
)

from infrastructure.db.models import Base
from infrastructure.db.models.common import intpk

if typing.TYPE_CHECKING:
    from infrastructure.db.models import Ingredient


class IngredientGroup(Base):
    __tablename__ = "ingredient_group"

    id: Mapped[intpk]
    title: Mapped[str]

    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary="ingredient_ingredient_group",
        back_populates="ingredient_groups"
    )

    def __repr__(self):
        return f"<IngredientGroup {self.id}: {self.title}>"
