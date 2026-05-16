import typing
from uuid import UUID

from sqlalchemy import TEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from domain.entities.value_objects import PubRecipeRequestStatus
from infrastructure.db.models import Base
from infrastructure.db.models.common import added_at, datetime_tz, intpk
from infrastructure.db.models.recipe import Recipe

if typing.TYPE_CHECKING:
    from infrastructure.db.models.user import User


class PubRecipeRequest(Base):
    __tablename__ = "pub_recipe_request"

    id: Mapped[intpk]
    feedback: Mapped[str] = mapped_column(TEXT(), nullable=True)
    status: Mapped[PubRecipeRequestStatus] = mapped_column(
        String(30),
        default=PubRecipeRequestStatus.pending.value
    )
    reviewed_at: Mapped[datetime_tz]
    created_at: Mapped[added_at]
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    moderator_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=True)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="pub_requests")
    author: Mapped["User"] = relationship(
        "User",
        foreign_keys=[author_id],
        back_populates="recipe_requests",
    )
    moderator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[moderator_id],
        back_populates="recipe_requests_reviewed",
    )
